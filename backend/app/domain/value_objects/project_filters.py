from dataclasses import dataclass


@dataclass(frozen=True)
class ProjectListFilters:
    status: str | None = None
    search: str | None = None
    page: int = 1
    limit: int = 20
