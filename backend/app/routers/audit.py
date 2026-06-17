from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from supabase import Client

from app.audit import actor_email, actor_full_name, can_record_client_action, write_audit_log
from app.auth import get_admin_client, get_current_user

router = APIRouter(prefix="/audit", tags=["audit"])


class AuditEventRequest(BaseModel):
    action: str = Field(min_length=1, max_length=80)
    resource: str | None = Field(default=None, max_length=200)
    details: dict[str, Any] = Field(default_factory=dict)


class AuditEventResponse(BaseModel):
    id: str
    action: str
    created_at: str


@router.post("/events", response_model=AuditEventResponse, status_code=status.HTTP_201_CREATED)
def record_audit_event(
    payload: AuditEventRequest,
    user=Depends(get_current_user),
    client: Client = Depends(get_admin_client),
) -> AuditEventResponse:
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

    return AuditEventResponse(
        id=str(row["id"]),
        action=str(row.get("action") or ""),
        created_at=str(row.get("created_at") or ""),
    )
