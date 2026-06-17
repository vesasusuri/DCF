from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any


@dataclass
class LatestRunInfo:
    run_number: int | None = None
    status: str | None = None
    completed_at: datetime | None = None
    created_at: datetime | None = None


@dataclass
class Project:
    id: str
    name: str
    organisation_id: str | None = None
    client: str | None = None
    currency: str = "EUR"
    valuation_date: date | None = None
    reporting_language: str = "de"
    status: str = "draft"
    team_name: str | None = None
    created_by: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ProjectSummary:
    id: str
    name: str
    client: str | None
    asset_count: int
    status: str
    latest_run: LatestRunInfo | None
    team_name: str | None
    created_at: datetime | None
    updated_at: datetime | None


@dataclass
class DashboardStats:
    open_projects: int
    assets_within_scope: int
    awaiting_review: int
    reports_per_month: int


@dataclass
class ProjectListResult:
    items: list[ProjectSummary]
    total: int
