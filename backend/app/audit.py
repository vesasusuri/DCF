import re
from typing import Any

from supabase import Client

ACTION_PATTERN = re.compile(r"^[a-z][a-z0-9]*(\.[a-z][a-z0-9_-]*){0,4}$")

SERVER_ONLY_ACTIONS = frozenset(
    {
        "user.created",
        "user.updated",
        "api.request",
    }
)

PUBLIC_CLIENT_ACTIONS = frozenset({"login", "logout"})

CLIENT_ACTION_PREFIXES = (
    "page.",
    "navigation.",
    "project.",
    "projects.",
    "upload.",
    "mapping.",
    "extraction.",
    "assumptions.",
    "runs.",
    "results.",
    "reports.",
    "dashboards.",
    "models.",
    "admin.",
)


def user_attr(user: Any, key: str, default: Any = None) -> Any:
    if isinstance(user, dict):
        return user.get(key, default)
    return getattr(user, key, default)


def actor_email(user: Any) -> str:
    return str(user_attr(user, "email") or "")


def actor_full_name(user: Any) -> str:
    metadata = user_attr(user, "user_metadata") or {}
    email = actor_email(user)
    if isinstance(metadata, dict):
        return metadata.get("full_name") or email.split("@")[0]
    return email.split("@")[0] if email else "Benutzer"


def can_record_client_action(action: str, *, role: str) -> bool:
    if action in SERVER_ONLY_ACTIONS:
        return False
    if not ACTION_PATTERN.match(action):
        return False
    if action in PUBLIC_CLIENT_ACTIONS:
        return True
    if action.startswith(CLIENT_ACTION_PREFIXES):
        return True
    if role == "admin":
        return action not in SERVER_ONLY_ACTIONS
    return False


def write_audit_log(
    client: Client,
    *,
    actor: Any,
    action: str,
    resource: str | None = None,
    details: dict[str, Any] | None = None,
) -> None:
    actor_id = user_attr(actor, "id")
    try:
        client.table("audit_logs").insert(
            {
                "actor_id": actor_id,
                "actor_email": actor_email(actor),
                "actor_name": actor_full_name(actor),
                "action": action,
                "resource": resource,
                "details": details or {},
            }
        ).execute()
    except Exception:
        pass
