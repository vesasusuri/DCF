from datetime import UTC, datetime
from math import ceil
import secrets
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from supabase import Client

from app.auth import get_admin_client, get_current_user, require_admin
from app.audit import (
    actor_email,
    actor_full_name,
    can_record_client_action,
    user_attr,
    write_audit_log,
)
from app.config import get_settings
from app.email_service import send_invite_email, smtp_configured

router = APIRouter(prefix="/admin", tags=["admin"])

AUDIT_PAGE_SIZE_DEFAULT = 25
AUDIT_PAGE_SIZE_MAX = 100


class AdminStatsResponse(BaseModel):
    users_total: int
    admins_total: int
    users_active_24h: int
    environment: str
    api_status: str


class AdminUserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    created_at: str | None
    last_sign_in_at: str | None
    must_change_password: bool = False
    email_verified: bool = False


class CreateAdminUserRequest(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=8)
    role: str = Field(default="user", pattern="^(user|admin)$")
    full_name: str = Field(min_length=1, max_length=120)


class InviteAdminUserRequest(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    role: str = Field(default="user", pattern="^(user|admin)$")
    full_name: str = Field(min_length=1, max_length=120)


class InviteAdminUserResponse(BaseModel):
    user: AdminUserResponse
    email_sent: bool
    message: str


class UpdateAdminUserRequest(BaseModel):
    role: str | None = Field(default=None, pattern="^(user|admin)$")
    full_name: str | None = Field(default=None, min_length=1, max_length=120)
    password: str | None = Field(default=None, min_length=8)


class AuditLogResponse(BaseModel):
    id: str
    actor_id: str | None
    actor_email: str | None
    actor_name: str | None
    action: str
    resource: str | None
    details: dict[str, Any]
    created_at: str


class PaginatedAuditLogsResponse(BaseModel):
    items: list[AuditLogResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class CreateAuditLogRequest(BaseModel):
    action: str = Field(min_length=1, max_length=80)
    resource: str | None = Field(default=None, max_length=200)
    details: dict[str, Any] = Field(default_factory=dict)


def _user_role(user: Any) -> str:
    metadata = user_attr(user, "user_metadata") or {}
    if isinstance(metadata, dict):
        return metadata.get("role", "user")
    return "user"


def _user_full_name(user: Any) -> str:
    return actor_full_name(user)


def _is_email_verified(user: Any) -> bool:
    metadata = user_attr(user, "user_metadata") or {}
    if isinstance(metadata, dict) and metadata.get("invited"):
        return bool(metadata.get("email_verified"))
    return bool(user_attr(user, "email_confirmed_at"))


def _to_iso_string(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


def _serialize_user(user: Any) -> AdminUserResponse:
    metadata = user_attr(user, "user_metadata") or {}

    return AdminUserResponse(
        id=str(user_attr(user, "id")),
        email=str(user_attr(user, "email") or ""),
        full_name=_user_full_name(user),
        role=_user_role(user),
        created_at=_to_iso_string(user_attr(user, "created_at")),
        last_sign_in_at=_to_iso_string(user_attr(user, "last_sign_in_at")),
        must_change_password=bool(metadata.get("must_change_password")),
        email_verified=_is_email_verified(user),
    )


def _generate_temporary_password() -> str:
    return f"Tmp-{secrets.token_urlsafe(9)}!"


def _list_all_users(client: Client) -> list[Any]:
    users: list[Any] = []
    page = 1
    while True:
        response = client.auth.admin.list_users(page=page, per_page=200)
        batch = response if isinstance(response, list) else getattr(response, "users", [])
        if not batch:
            break
        users.extend(batch)
        if len(batch) < 200:
            break
        page += 1
    return users


@router.get("/stats", response_model=AdminStatsResponse)
def get_admin_stats(
    _admin=Depends(require_admin),
    client: Client = Depends(get_admin_client),
) -> AdminStatsResponse:
    settings = get_settings()
    users = _list_all_users(client)
    admins = [user for user in users if _user_role(user) == "admin"]

    active_24h = 0
    cutoff = datetime.now(UTC).timestamp() - 24 * 60 * 60
    for user in users:
        last_sign_in = user_attr(user, "last_sign_in_at")
        if not last_sign_in:
            continue
        try:
            last_dt = datetime.fromisoformat(str(last_sign_in).replace("Z", "+00:00"))
            if last_dt.timestamp() >= cutoff:
                active_24h += 1
        except ValueError:
            continue

    return AdminStatsResponse(
        users_total=len(users),
        admins_total=len(admins),
        users_active_24h=active_24h,
        environment=settings.app_env,
        api_status="ok",
    )


@router.get("/users", response_model=list[AdminUserResponse])
def list_admin_users(
    _admin=Depends(require_admin),
    client: Client = Depends(get_admin_client),
) -> list[AdminUserResponse]:
    users = _list_all_users(client)
    users.sort(key=lambda user: _user_full_name(user).lower())
    return [_serialize_user(user) for user in users]


@router.post("/users/invite", response_model=InviteAdminUserResponse, status_code=status.HTTP_201_CREATED)
def invite_admin_user(
    payload: InviteAdminUserRequest,
    admin=Depends(require_admin),
    client: Client = Depends(get_admin_client),
) -> InviteAdminUserResponse:
    settings = get_settings()
    temporary_password = _generate_temporary_password()
    login_url = f"{settings.app_public_url.rstrip('/')}/login"

    try:
        created = client.auth.admin.create_user(
            {
                "email": payload.email,
                "password": temporary_password,
                "email_confirm": True,
                "user_metadata": {
                    "role": payload.role,
                    "full_name": payload.full_name,
                    "must_change_password": True,
                    "invited": True,
                    "email_verified": False,
                },
            }
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not invite user: {exc}",
        ) from exc

    user = created.user
    user_id = user_attr(user, "id")
    if user_id:
        try:
            client.table("profiles").upsert(
                {
                    "id": user_id,
                    "email": payload.email,
                    "full_name": payload.full_name,
                    "role": payload.role,
                }
            ).execute()
        except Exception:
            pass

    email_sent = send_invite_email(
        to_email=payload.email,
        full_name=payload.full_name,
        temporary_password=temporary_password,
        login_url=login_url,
        settings=settings,
    )

    write_audit_log(
        client,
        actor=admin,
        action="user.invited",
        resource=payload.email,
        details={"role": payload.role, "full_name": payload.full_name, "email_sent": email_sent},
    )

    if email_sent:
        message = "Einladung wurde per E-Mail versendet."
    elif smtp_configured(settings):
        message = "Benutzer wurde angelegt, aber die E-Mail konnte nicht gesendet werden."
    else:
        message = (
            "Benutzer wurde angelegt. SMTP ist nicht konfiguriert — "
            "bitte Zugangsdaten manuell übermitteln."
        )

    return InviteAdminUserResponse(
        user=_serialize_user(user),
        email_sent=email_sent,
        message=message,
    )


@router.get("/logs", response_model=PaginatedAuditLogsResponse)
def list_audit_logs(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=AUDIT_PAGE_SIZE_DEFAULT, ge=1, le=AUDIT_PAGE_SIZE_MAX),
    _admin=Depends(require_admin),
    client: Client = Depends(get_admin_client),
) -> PaginatedAuditLogsResponse:
    offset = (page - 1) * page_size
    end = offset + page_size - 1

    try:
        response = (
            client.table("audit_logs")
            .select("*", count="exact")
            .order("created_at", desc=True)
            .range(offset, end)
            .execute()
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Audit logs are not available: {exc}",
        ) from exc

    rows = response.data or []
    total = int(response.count or 0)
    total_pages = max(1, ceil(total / page_size)) if total else 0

    items = [
        AuditLogResponse(
            id=str(row["id"]),
            actor_id=row.get("actor_id"),
            actor_email=row.get("actor_email"),
            actor_name=row.get("actor_name"),
            action=str(row.get("action") or ""),
            resource=row.get("resource"),
            details=row.get("details") or {},
            created_at=str(row.get("created_at") or ""),
        )
        for row in rows
    ]

    return PaginatedAuditLogsResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.post("/logs", response_model=AuditLogResponse, status_code=status.HTTP_201_CREATED)
def create_audit_log(
    payload: CreateAuditLogRequest,
    user=Depends(get_current_user),
    client: Client = Depends(get_admin_client),
) -> AuditLogResponse:
    role = (getattr(user, "user_metadata", None) or {}).get("role", "user")
    if not can_record_client_action(payload.action, role=role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to record this audit event.",
        )

    try:
        inserted = (
            client.table("audit_logs")
            .insert(
                {
                    "actor_id": user.id,
                    "actor_email": actor_email(user),
                    "actor_name": actor_full_name(user),
                    "action": payload.action,
                    "resource": payload.resource,
                    "details": payload.details,
                }
            )
            .execute()
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Could not write audit log: {exc}",
        ) from exc

    row = (inserted.data or [None])[0]
    if not row:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Audit log was not created.",
        )

    return AuditLogResponse(
        id=str(row["id"]),
        actor_id=row.get("actor_id"),
        actor_email=row.get("actor_email"),
        actor_name=row.get("actor_name"),
        action=str(row.get("action") or ""),
        resource=row.get("resource"),
        details=row.get("details") or {},
        created_at=str(row.get("created_at") or ""),
    )


@router.post("/users", response_model=AdminUserResponse, status_code=status.HTTP_201_CREATED)
def create_admin_user(
    payload: CreateAdminUserRequest,
    admin=Depends(require_admin),
    client: Client = Depends(get_admin_client),
) -> AdminUserResponse:
    try:
        created = client.auth.admin.create_user(
            {
                "email": payload.email,
                "password": payload.password,
                "email_confirm": True,
                "user_metadata": {
                    "role": payload.role,
                    "full_name": payload.full_name,
                },
            }
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not create user: {exc}",
        ) from exc

    user = created.user
    user_id = user_attr(user, "id")
    if user_id:
        try:
            client.table("profiles").upsert(
                {
                    "id": user_id,
                    "email": payload.email,
                    "full_name": payload.full_name,
                    "role": payload.role,
                }
            ).execute()
        except Exception:
            pass

    write_audit_log(
        client,
        actor=admin,
        action="user.created",
        resource=payload.email,
        details={"role": payload.role, "full_name": payload.full_name},
    )

    return _serialize_user(user)


@router.patch("/users/{user_id}", response_model=AdminUserResponse)
def update_admin_user(
    user_id: str,
    payload: UpdateAdminUserRequest,
    admin=Depends(require_admin),
    client: Client = Depends(get_admin_client),
) -> AdminUserResponse:
    update_data: dict[str, Any] = {}
    metadata: dict[str, Any] = {}

    if payload.role is not None:
        metadata["role"] = payload.role
    if payload.full_name is not None:
        metadata["full_name"] = payload.full_name
    if payload.password is not None:
        update_data["password"] = payload.password

    if metadata:
        try:
            existing = client.auth.admin.get_user_by_id(user_id)
            existing_meta = getattr(existing.user, "user_metadata", None) or {}
            if isinstance(existing_meta, dict):
                metadata = {**existing_meta, **metadata}
        except Exception:
            pass
        update_data["user_metadata"] = metadata

    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No changes provided.")

    try:
        updated = client.auth.admin.update_user_by_id(user_id, update_data)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not update user: {exc}",
        ) from exc

    user = updated.user
    if payload.role is not None or payload.full_name is not None:
        try:
            client.table("profiles").upsert(
                {
                    "id": user_id,
                    "email": user_attr(user, "email"),
                    "full_name": _user_full_name(user),
                    "role": _user_role(user),
                }
            ).execute()
        except Exception:
            pass

    audit_details: dict[str, Any] = {}
    if payload.role is not None:
        audit_details["role"] = payload.role
    if payload.full_name is not None:
        audit_details["full_name"] = payload.full_name
    if payload.password is not None:
        audit_details["password_changed"] = True

    if audit_details:
        write_audit_log(
            client,
            actor=admin,
            action="user.updated",
            resource=actor_email(user),
            details=audit_details,
        )

    return _serialize_user(user)
