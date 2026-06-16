from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.domain.entities.portfolio_manager import PortfolioManagerAssignment
from app.domain.interfaces.repositories import IPortfolioManagerRepository
from app.infrastructure.models.profile_model import ProfileModel, ProjectPortfolioManagerModel


class SqlPortfolioManagerRepository(IPortfolioManagerRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_assignment(self, project_id: str, user_id: str) -> PortfolioManagerAssignment | None:
        stmt = self._assignment_query().where(
            ProjectPortfolioManagerModel.project_id == UUID(project_id),
            ProjectPortfolioManagerModel.user_id == UUID(user_id),
        )
        result = await self._session.execute(stmt)
        row = result.one_or_none()
        return self._to_domain(*row) if row else None

    async def list_by_project(self, project_id: str) -> list[PortfolioManagerAssignment]:
        stmt = self._assignment_query().where(
            ProjectPortfolioManagerModel.project_id == UUID(project_id),
        ).order_by(ProjectPortfolioManagerModel.assigned_at.desc())
        result = await self._session.execute(stmt)
        return [self._to_domain(assignment, profile) for assignment, profile in result.all()]

    async def list_by_user(self, user_id: str) -> list[PortfolioManagerAssignment]:
        stmt = self._assignment_query().where(
            ProjectPortfolioManagerModel.user_id == UUID(user_id),
        ).order_by(ProjectPortfolioManagerModel.assigned_at.desc())
        result = await self._session.execute(stmt)
        return [self._to_domain(assignment, profile) for assignment, profile in result.all()]

    async def create_assignment(
        self,
        project_id: str,
        user_id: str,
        assigned_by: str | None,
    ) -> PortfolioManagerAssignment:
        model = ProjectPortfolioManagerModel(
            project_id=UUID(project_id),
            user_id=UUID(user_id),
            assigned_by=UUID(assigned_by) if assigned_by else None,
        )
        self._session.add(model)
        await self._session.flush()
        assignment = await self.get_assignment(project_id, user_id)
        if not assignment:
            raise RuntimeError("Failed to create portfolio manager assignment")
        return assignment

    async def update_assignment(
        self,
        project_id: str,
        user_id: str,
        assigned_by: str | None,
    ) -> PortfolioManagerAssignment:
        stmt = select(ProjectPortfolioManagerModel).where(
            ProjectPortfolioManagerModel.project_id == UUID(project_id),
            ProjectPortfolioManagerModel.user_id == UUID(user_id),
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one()
        model.assigned_by = UUID(assigned_by) if assigned_by else None
        await self._session.flush()
        assignment = await self.get_assignment(project_id, user_id)
        if not assignment:
            raise RuntimeError("Failed to update portfolio manager assignment")
        return assignment

    async def delete_assignment(self, project_id: str, user_id: str) -> None:
        stmt = delete(ProjectPortfolioManagerModel).where(
            ProjectPortfolioManagerModel.project_id == UUID(project_id),
            ProjectPortfolioManagerModel.user_id == UUID(user_id),
        )
        await self._session.execute(stmt)

    @staticmethod
    def _assignment_query():
        profile = aliased(ProfileModel)
        return select(ProjectPortfolioManagerModel, profile).join(
            profile,
            profile.id == ProjectPortfolioManagerModel.user_id,
        )

    @staticmethod
    def _to_domain(
        assignment: ProjectPortfolioManagerModel,
        profile: ProfileModel,
    ) -> PortfolioManagerAssignment:
        return PortfolioManagerAssignment(
            id=str(assignment.id),
            project_id=str(assignment.project_id),
            user_id=str(assignment.user_id),
            assigned_by=str(assignment.assigned_by) if assignment.assigned_by else None,
            assigned_at=assignment.assigned_at,
            user_email=profile.email,
            user_full_name=profile.full_name,
        )
