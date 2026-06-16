from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class AuditEvent:
    id: str
    entity_type: str
    entity_id: str
    action: str
    user_id: str
    payload: dict[str, Any]
    created_at: datetime
