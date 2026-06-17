from math import ceil
from typing import Any

from app.domain.constants import PROJECT_STATUSES, PROJECT_STATUS_DRAFT
from app.domain.entities.project import LatestRunInfo, Project, ProjectSummary
from app.domain.exceptions import InvalidProjectError, ProjectNotFoundError
from app.domain.interfaces.repositories import IProjectRepository
from app.domain.value_objects.project_filters import ProjectListFilters


class ProjectService:
    def __init__(self, project_repo: IProjectRepository) -> None:
        self._project_repo = project_repo

    async def list_projects(
        self,
        *,
        page: int = 1,
        limit: int = 20,
        status: str | None = None,
        search: str | None = None,
    ) -> dict[str, Any]:
        normalized_status = self._normalize_status_filter(status)
        filters = ProjectListFilters(
            status=normalized_status,
            search=search,
            page=page,
            limit=limit,
        )
        result = await self._project_repo.list_summaries(filters)
        pages = 0 if result.total == 0 else ceil(result.total / min(max(limit, 1), 100))
        return {
            "items": [self._summary_to_dict(item) for item in result.items],
            "total": result.total,
            "page": max(page, 1),
            "pages": pages,
        }

    async def get_project(self, project_id: str) -> dict[str, Any]:
        project = await self._project_repo.get_by_id(project_id)
        if not project:
            raise ProjectNotFoundError(project_id)
        return self._detail_to_dict(project)

    async def create_project(
        self,
        *,
        client: str,
        project_name: str,
        currency: str,
        valuation_date,
        reporting_language: str,
        created_by: str,
    ) -> dict[str, Any]:
        project = Project(
            id="",
            name=project_name.strip(),
            client=client.strip(),
            currency=currency.upper(),
            valuation_date=valuation_date,
            reporting_language=reporting_language.strip(),
            status=PROJECT_STATUS_DRAFT,
            created_by=created_by,
        )
        saved = await self._project_repo.save(project)
        return self._detail_to_dict(saved)

    async def update_project(self, project_id: str, updates: dict[str, Any]) -> dict[str, Any]:
        project = await self._project_repo.get_by_id(project_id)
        if not project:
            raise ProjectNotFoundError(project_id)

        if "project_name" in updates and updates["project_name"] is not None:
            project.name = updates["project_name"].strip()
        if "client" in updates and updates["client"] is not None:
            project.client = updates["client"].strip()
        if "currency" in updates and updates["currency"] is not None:
            project.currency = updates["currency"].upper()
        if "valuation_date" in updates:
            project.valuation_date = updates["valuation_date"]
        if "reporting_language" in updates and updates["reporting_language"] is not None:
            project.reporting_language = updates["reporting_language"].strip()
        if "status" in updates and updates["status"] is not None:
            status = updates["status"].lower()
            if status not in PROJECT_STATUSES:
                raise InvalidProjectError(f"Invalid project status: {updates['status']}")
            project.status = status
        if "assigned_team" in updates:
            team = updates["assigned_team"]
            project.team_name = team.strip() if team else None

        saved = await self._project_repo.save(project)
        return self._detail_to_dict(saved)

    @staticmethod
    def _normalize_status_filter(status: str | None) -> str | None:
        if not status or status.lower() == "all":
            return None
        normalized = status.lower()
        if normalized not in {"active", "archived"}:
            raise InvalidProjectError(f"Invalid status filter: {status}")
        return normalized

    @staticmethod
    def _iso(value) -> str | None:
        if value is None:
            return None
        return value.isoformat()

    def _summary_to_dict(self, summary: ProjectSummary) -> dict[str, Any]:
        latest_run = None
        if summary.latest_run:
            latest_run = self._latest_run_to_dict(summary.latest_run)
        return {
            "id": summary.id,
            "projectName": summary.name,
            "clientName": summary.client,
            "assetCount": summary.asset_count,
            "status": summary.status,
            "latestRun": latest_run,
            "assignedTeam": summary.team_name,
            "createdAt": self._iso(summary.created_at),
            "updatedAt": self._iso(summary.updated_at),
        }

    def _detail_to_dict(self, project: Project) -> dict[str, Any]:
        return {
            "id": project.id,
            "projectName": project.name,
            "clientName": project.client,
            "currency": project.currency,
            "valuationDate": self._iso(project.valuation_date),
            "reportingLanguage": project.reporting_language,
            "status": project.status,
            "assignedTeam": project.team_name,
            "createdBy": project.created_by,
            "createdAt": self._iso(project.created_at),
            "updatedAt": self._iso(project.updated_at),
            "metadata": project.metadata,
        }

    @staticmethod
    def _latest_run_to_dict(run: LatestRunInfo) -> dict[str, Any]:
        return {
            "runNumber": run.run_number,
            "status": run.status,
            "completedAt": run.completed_at.isoformat() if run.completed_at else None,
            "createdAt": run.created_at.isoformat() if run.created_at else None,
        }
