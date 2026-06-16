from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from app.domain.value_objects.date_range import DateRange
from app.domain.value_objects.money import Money


@dataclass
class Lease:
    id: str
    tenant_name: str
    unit_id: str
    term: DateRange
    passing_rent: Money
    indexation_type: str = "none"
    indexation_rate: Decimal | None = None
    break_option_date: date | None = None
    has_extension_option: bool = False

    def is_active(self, as_of: date) -> bool:
        return self.term.contains(as_of)

    def months_to_expiry(self, as_of: date) -> int:
        return self.term.months_until_end(as_of)
