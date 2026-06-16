from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any


@dataclass
class Project:
    id: str
    name: str
    organisation_id: str | None = None
    client: str | None = None
    currency: str = "EUR"
    valuation_date: date | None = None
    status: str = "draft"
    created_by: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
