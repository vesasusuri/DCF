from dataclasses import asdict
from typing import Any

from app.domain.entities.project import Project
from app.domain.exceptions import ProjectNotFoundError
from app.domain.interfaces.repositories import IProjectRepository


class ProjectService:
    def __init__(self, project_repo: IProjectRepository) -> None:
        self._project_repo = project_repo

    async def list_projects(self, limit: int = 20) -> list[dict[str, Any]]:
        projects = await self._project_repo.list_all(limit=limit)
        return [self._to_dict(p) for p in projects]

    async def get_project(self, project_id: str) -> dict[str, Any]:
        project = await self._project_repo.get_by_id(project_id)
        if not project:
            raise ProjectNotFoundError(project_id)
        return self._to_dict(project)

    @staticmethod
    def _to_dict(project: Project) -> dict[str, Any]:
        data = asdict(project)
        for key in ("created_at", "updated_at", "valuation_date"):
            if data.get(key) is not None:
                data[key] = data[key].isoformat()
        return data
