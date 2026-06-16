from app.domain.exceptions import ProjectNotFoundError
from app.domain.interfaces.repositories import IProjectRepository


class ValuationRunService:
    """Stub — triggers valuation runs."""

    def __init__(self, project_repo: IProjectRepository) -> None:
        self._project_repo = project_repo

    async def execute(self, project_id: str, scenario_id: str, user_id: str) -> str:
        project = await self._project_repo.get_by_id(project_id)
        if not project:
            raise ProjectNotFoundError(project_id)
        raise NotImplementedError("Valuation run orchestration not yet implemented")
