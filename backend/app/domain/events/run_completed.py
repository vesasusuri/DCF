from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class RunCompleted:
    run_id: str
    project_id: str
    completed_at: datetime
