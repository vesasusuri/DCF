from dataclasses import dataclass
from typing import Any


@dataclass
class AssumptionSet:
    id: str
    project_id: str
    name: str
    assumptions: dict[str, Any]
