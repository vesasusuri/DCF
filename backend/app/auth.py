from fastapi import Depends, Header, HTTPException, status
from supabase import Client, create_client

from app.config import Settings, get_settings
from app.database import get_supabase_client


def get_bearer_token(authorization: str | None = Header(default=None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing or invalid.",
        )
    return authorization.removeprefix("Bearer ").strip()


def get_auth_client(settings: Settings = Depends(get_settings)) -> Client:
    if not settings.supabase_url or not settings.supabase_anon_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Supabase auth is not configured.",
        )
    return create_client(settings.supabase_url, settings.supabase_anon_key)


def get_current_user(
    token: str = Depends(get_bearer_token),
    auth_client: Client = Depends(get_auth_client),
):
    try:
        response = auth_client.auth.get_user(token)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session.",
        ) from exc

    if not response or not response.user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session.",
        )

    return response.user


def require_admin(user=Depends(get_current_user)):
    role = (user.user_metadata or {}).get("role")
    if role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required.",
        )
    return user


def get_admin_client() -> Client:
    client = get_supabase_client()
    if client is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Supabase service client is not configured.",
        )
    return client
