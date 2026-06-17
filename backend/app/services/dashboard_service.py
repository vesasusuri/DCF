from typing import Any

from app.domain.interfaces.repositories import IProjectRepository


class DashboardService:
    def __init__(self, project_repo: IProjectRepository) -> None:
        self._project_repo = project_repo

    async def get_stats(self) -> dict[str, Any]:
        stats = await self._project_repo.get_dashboard_stats()
        return {
            "openProjects": stats.open_projects,
            "assetsWithinScope": stats.assets_within_scope,
            "awaitingReview": stats.awaiting_review,
            "reportsPerMonth": stats.reports_per_month,
        }
