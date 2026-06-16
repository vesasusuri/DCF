from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class AssumptionChanged:
    project_id: str
    assumption_id: str
    changed_by: str
    changed_at: datetime
