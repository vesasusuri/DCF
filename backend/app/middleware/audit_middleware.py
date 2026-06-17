from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.audit import write_audit_log
from app.auth import get_auth_client
from app.database import get_supabase_client

def _should_audit(path: str, method: str) -> bool:
    if not path.startswith("/api/v1"):
        return False
    if method == "OPTIONS":
        return False
    if path.endswith("/health"):
        return False
    if "/admin/logs" in path:
        return False
    if path.endswith("/audit/events"):
        return False
    return True


def _resolve_user(token: str) -> Any | None:
    try:
        client = get_auth_client()
        response = client.auth.get_user(token)
        return response.user if response else None
    except Exception:
        return None


class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)

        path = request.url.path
        method = request.method.upper()
        if not _should_audit(path, method):
            return response

        authorization = request.headers.get("authorization", "")
        if not authorization.startswith("Bearer "):
            return response

        token = authorization.removeprefix("Bearer ").strip()
        user = _resolve_user(token)
        if not user:
            return response

        client = get_supabase_client()
        if client is None:
            return response

        try:
            write_audit_log(
                client,
                actor=user,
                action="api.request",
                resource=f"{method} {path}",
                details={
                    "method": method,
                    "path": path,
                    "status_code": response.status_code,
                    "query": str(request.url.query) if request.url.query else None,
                },
            )
        except Exception:
            pass
        return response
