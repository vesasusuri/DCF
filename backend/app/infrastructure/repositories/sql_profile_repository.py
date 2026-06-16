from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.portfolio_manager import UserProfile
from app.domain.interfaces.repositories import IProfileRepository
from app.infrastructure.models.profile_model import ProfileModel


class SqlProfileRepository(IProfileRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, user_id: str) -> UserProfile | None:
        model = await self._session.get(ProfileModel, user_id)
        return self._to_domain(model) if model else None

    async def get_by_email(self, email: str) -> UserProfile | None:
        stmt = select(ProfileModel).where(ProfileModel.email == email)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def list_by_role(self, role: str) -> list[UserProfile]:
        stmt = select(ProfileModel).where(ProfileModel.role == role).order_by(ProfileModel.email)
        result = await self._session.execute(stmt)
        return [self._to_domain(row) for row in result.scalars().all()]

    @staticmethod
    def _to_domain(model: ProfileModel) -> UserProfile:
        return UserProfile(
            id=str(model.id),
            email=model.email,
            full_name=model.full_name,
            role=model.role,
            created_at=model.created_at,
        )
