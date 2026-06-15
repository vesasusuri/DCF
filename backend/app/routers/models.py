from fastapi import APIRouter, HTTPException
from supabase import Client

from app.database import get_supabase_client

router = APIRouter(prefix="/models", tags=["models"])


@router.get("")
def list_models() -> dict:
    client: Client | None = get_supabase_client()
    if client is None:
        raise HTTPException(
            status_code=503,
            detail="Supabase is not configured. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY.",
        )

    response = client.table("dcf_models").select("*").limit(20).execute()
    return {"data": response.data}
