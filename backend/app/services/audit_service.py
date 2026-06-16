from typing import Any

from app.domain.interfaces.repositories import IAuditRepository


class AuditService:
    def __init__(self, audit_repo: IAuditRepository) -> None:
        self._audit_repo = audit_repo

    async def record_portfolio_manager_created(
        self,
        *,
        user_id: str,
        email: str,
        actor_id: str,
    ) -> None:
        await self._audit_repo.record(
            entity_type="portfolio_manager",
            entity_id=user_id,
            action="create",
            user_id=actor_id,
            new_value=email,
            payload={"email": email},
        )

    async def record_assignment_created(
        self,
        *,
        project_id: str,
        user_id: str,
        actor_id: str,
        payload: dict[str, Any] | None = None,
    ) -> None:
        await self._audit_repo.record(
            entity_type="portfolio_manager_assignment",
            entity_id=f"{project_id}:{user_id}",
            action="create",
            user_id=actor_id,
            project_id=project_id,
            new_value=user_id,
            payload=payload or {},
        )

    async def record_assignment_updated(
        self,
        *,
        project_id: str,
        user_id: str,
        actor_id: str,
        payload: dict[str, Any] | None = None,
    ) -> None:
        await self._audit_repo.record(
            entity_type="portfolio_manager_assignment",
            entity_id=f"{project_id}:{user_id}",
            action="update",
            user_id=actor_id,
            project_id=project_id,
            payload=payload or {},
        )

    async def record_assignment_removed(
        self,
        *,
        project_id: str,
        user_id: str,
        actor_id: str,
        payload: dict[str, Any] | None = None,
    ) -> None:
        await self._audit_repo.record(
            entity_type="portfolio_manager_assignment",
            entity_id=f"{project_id}:{user_id}",
            action="delete",
            user_id=actor_id,
            project_id=project_id,
            old_value=user_id,
            payload=payload or {},
        )
