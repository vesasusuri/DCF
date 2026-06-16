from dataclasses import dataclass
from datetime import datetime


@dataclass
class PortfolioManagerAssignment:
    id: str
    project_id: str
    user_id: str
    assigned_by: str | None
    assigned_at: datetime
    user_email: str | None = None
    user_full_name: str | None = None


@dataclass
class UserProfile:
    id: str
    email: str
    full_name: str | None
    role: str
    created_at: datetime | None = None
