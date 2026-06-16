from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from supabase import Client

from app.auth import get_admin_client, require_admin
from app.config import get_settings

router = APIRouter(prefix="/admin", tags=["admin"])


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


class CreateAdminUserRequest(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=8)
    role: str = Field(default="user", pattern="^(user|admin)$")
    full_name: str = Field(min_length=1, max_length=120)


class UpdateAdminUserRequest(BaseModel):
    role: str | None = Field(default=None, pattern="^(user|admin)$")
    full_name: str | None = Field(default=None, min_length=1, max_length=120)
    password: str | None = Field(default=None, min_length=8)


def _user_role(user: Any) -> str:
    metadata = getattr(user, "user_metadata", None) or user.get("user_metadata") or {}
    if isinstance(metadata, dict):
        return metadata.get("role", "user")
    return "user"


def _user_full_name(user: Any) -> str:
    metadata = getattr(user, "user_metadata", None) or user.get("user_metadata") or {}
    email = getattr(user, "email", None) or user.get("email") or ""
    if isinstance(metadata, dict):
        return metadata.get("full_name") or email.split("@")[0]
    return email.split("@")[0]


def _serialize_user(user: Any) -> AdminUserResponse:
    return AdminUserResponse(
        id=str(getattr(user, "id", None) or user.get("id")),
        email=str(getattr(user, "email", None) or user.get("email") or ""),
        full_name=_user_full_name(user),
        role=_user_role(user),
        created_at=getattr(user, "created_at", None) or user.get("created_at"),
        last_sign_in_at=getattr(user, "last_sign_in_at", None) or user.get("last_sign_in_at"),
    )


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
        last_sign_in = getattr(user, "last_sign_in_at", None) or user.get("last_sign_in_at")
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


@router.post("/users", response_model=AdminUserResponse, status_code=status.HTTP_201_CREATED)
def create_admin_user(
    payload: CreateAdminUserRequest,
    _admin=Depends(require_admin),
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
    user_id = getattr(user, "id", None) or user.get("id")
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

    return _serialize_user(user)


@router.patch("/users/{user_id}", response_model=AdminUserResponse)
def update_admin_user(
    user_id: str,
    payload: UpdateAdminUserRequest,
    _admin=Depends(require_admin),
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
                    "email": getattr(user, "email", None) or user.get("email"),
                    "full_name": _user_full_name(user),
                    "role": _user_role(user),
                }
            ).execute()
        except Exception:
            pass

    return _serialize_user(user)
