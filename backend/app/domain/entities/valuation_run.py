from dataclasses import dataclass
from datetime import datetime


@dataclass
class ValuationRun:
    id: str
    project_id: str
    scenario_id: str
    status: str
    triggered_by: str
    created_at: datetime
