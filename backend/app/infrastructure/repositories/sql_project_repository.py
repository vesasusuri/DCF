from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.project import Project
from app.domain.interfaces.repositories import IProjectRepository
from app.infrastructure.models.project_model import DcfModel


class SqlProjectRepository(IProjectRepository):
    """Transitional repository using dcf_models table until full schema migration."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, project_id: str) -> Project | None:
        result = await self._session.get(DcfModel, project_id)
        return self._to_domain(result) if result else None

    async def save(self, project: Project) -> None:
        raise NotImplementedError("Project persistence not yet implemented")

    async def list_by_organisation(self, org_id: str) -> list[Project]:
        return await self.list_all()

    async def list_all(self, limit: int = 20) -> list[Project]:
        stmt = select(DcfModel).limit(limit)
        result = await self._session.execute(stmt)
        return [self._to_domain(row) for row in result.scalars().all()]

    @staticmethod
    def _to_domain(model: DcfModel) -> Project:
        return Project(
            id=str(model.id),
            name=model.name,
            metadata={"ticker": model.ticker, "assumptions": model.assumptions},
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
