from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Asset:
    id: str
    project_id: str
    name: str
    address: str | None = None
    city: str | None = None
    postal_code: str | None = None
    gla_sqm: Decimal | None = None
