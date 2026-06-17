from fastapi import APIRouter, Depends, HTTPException
from supabase import Client

from app.audit import write_audit_log
from app.auth import get_current_user
from app.database import get_supabase_client

router = APIRouter(prefix="/models", tags=["models"])


@router.get("")
def list_models(user=Depends(get_current_user)) -> dict:
    client: Client | None = get_supabase_client()
    if client is None:
        raise HTTPException(
            status_code=503,
            detail="Supabase is not configured. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY.",
        )

    response = client.table("dcf_models").select("*").limit(20).execute()

    write_audit_log(
        client,
        actor=user,
        action="models.list",
        resource="dcf_models",
        details={"count": len(response.data or [])},
    )

    return {"data": response.data}
