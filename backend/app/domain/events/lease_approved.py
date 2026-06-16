from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class LeaseApproved:
    lease_id: str
    project_id: str
    approved_by: str
    approved_at: datetime
