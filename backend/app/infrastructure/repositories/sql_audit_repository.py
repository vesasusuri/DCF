from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.interfaces.repositories import IAuditRepository
from app.infrastructure.models.profile_model import AuditEventModel


class SqlAuditRepository(IAuditRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def record(
        self,
        *,
        entity_type: str,
        entity_id: str,
        action: str,
        user_id: str | None,
        project_id: str | None = None,
        field: str | None = None,
        old_value: str | None = None,
        new_value: str | None = None,
        reason: str | None = None,
        payload: dict | None = None,
    ) -> None:
        event = AuditEventModel(
            project_id=UUID(project_id) if project_id else None,
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            field=field,
            old_value=old_value,
            new_value=new_value,
            reason=reason,
            user_id=UUID(user_id) if user_id else None,
            payload=payload or {},
        )
        self._session.add(event)
        await self._session.flush()
