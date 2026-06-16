import logging
from typing import Any

from supabase import Client, create_client

from app.core.auth import PORTFOLIO_MANAGER_ROLE
from app.core.config import get_settings
from app.domain.entities.portfolio_manager import PortfolioManagerAssignment, UserProfile
from app.domain.exceptions import (
    AssignmentNotFoundError,
    DuplicateAssignmentError,
    NotPortfolioManagerError,
    ProjectNotFoundError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from app.domain.interfaces.repositories import (
    IPortfolioManagerRepository,
    IProfileRepository,
    IProjectRepository,
)
from app.services.audit_service import AuditService

logger = logging.getLogger(__name__)


class PortfolioManagerService:
    def __init__(
        self,
        *,
        profile_repo: IProfileRepository,
        assignment_repo: IPortfolioManagerRepository,
        project_repo: IProjectRepository,
        audit_service: AuditService,
        supabase_admin: Client | None = None,
    ) -> None:
        self._profile_repo = profile_repo
        self._assignment_repo = assignment_repo
        self._project_repo = project_repo
        self._audit_service = audit_service
        self._supabase_admin = supabase_admin

    async def create_portfolio_manager(
        self,
        *,
        email: str,
        password: str,
        full_name: str,
        actor_id: str,
    ) -> dict[str, Any]:
        existing = await self._profile_repo.get_by_email(email)
        if existing:
            raise UserAlreadyExistsError(email)

        user_id = await self._create_supabase_user(
            email=email,
            password=password,
            full_name=full_name,
        )
        profile = await self._profile_repo.get_by_id(user_id)
        if profile is None:
            raise UserNotFoundError(user_id)

        await self._audit_service.record_portfolio_manager_created(
            user_id=user_id,
            email=email,
            actor_id=actor_id,
        )
        return self._profile_to_dict(profile)

    async def list_portfolio_managers(self) -> list[dict[str, Any]]:
        profiles = await self._profile_repo.list_by_role(PORTFOLIO_MANAGER_ROLE)
        return [self._profile_to_dict(profile) for profile in profiles]

    async def list_project_assignments(self, project_id: str) -> list[dict[str, Any]]:
        await self._ensure_project_exists(project_id)
        assignments = await self._assignment_repo.list_by_project(project_id)
        return [self._assignment_to_dict(assignment) for assignment in assignments]

    async def assign_to_project(
        self,
        *,
        project_id: str,
        user_id: str,
        actor_id: str,
    ) -> dict[str, Any]:
        await self._ensure_project_exists(project_id)
        profile = await self._ensure_portfolio_manager(user_id)

        existing = await self._assignment_repo.get_assignment(project_id, user_id)
        if existing:
            raise DuplicateAssignmentError(project_id, user_id)

        assignment = await self._assignment_repo.create_assignment(
            project_id=project_id,
            user_id=user_id,
            assigned_by=actor_id,
        )
        await self._audit_service.record_assignment_created(
            project_id=project_id,
            user_id=user_id,
            actor_id=actor_id,
            payload={
                "user_email": profile.email,
                "user_full_name": profile.full_name,
            },
        )
        return self._assignment_to_dict(assignment)

    async def update_assignment(
        self,
        *,
        project_id: str,
        user_id: str,
        actor_id: str,
    ) -> dict[str, Any]:
        await self._ensure_project_exists(project_id)
        profile = await self._ensure_portfolio_manager(user_id)

        existing = await self._assignment_repo.get_assignment(project_id, user_id)
        if not existing:
            raise AssignmentNotFoundError(project_id, user_id)

        assignment = await self._assignment_repo.update_assignment(
            project_id=project_id,
            user_id=user_id,
            assigned_by=actor_id,
        )
        await self._audit_service.record_assignment_updated(
            project_id=project_id,
            user_id=user_id,
            actor_id=actor_id,
            payload={
                "user_email": profile.email,
                "user_full_name": profile.full_name,
            },
        )
        return self._assignment_to_dict(assignment)

    async def remove_assignment(
        self,
        *,
        project_id: str,
        user_id: str,
        actor_id: str,
    ) -> None:
        await self._ensure_project_exists(project_id)
        existing = await self._assignment_repo.get_assignment(project_id, user_id)
        if not existing:
            raise AssignmentNotFoundError(project_id, user_id)

        await self._assignment_repo.delete_assignment(project_id, user_id)
        await self._audit_service.record_assignment_removed(
            project_id=project_id,
            user_id=user_id,
            actor_id=actor_id,
            payload={
                "user_email": existing.user_email,
                "user_full_name": existing.user_full_name,
            },
        )

    async def _ensure_project_exists(self, project_id: str) -> None:
        project = await self._project_repo.get_by_id(project_id)
        if not project:
            raise ProjectNotFoundError(project_id)

    async def _ensure_portfolio_manager(self, user_id: str) -> UserProfile:
        profile = await self._profile_repo.get_by_id(user_id)
        if not profile:
            raise UserNotFoundError(user_id)
        if profile.role != PORTFOLIO_MANAGER_ROLE:
            raise NotPortfolioManagerError(user_id)
        return profile

    async def _create_supabase_user(self, *, email: str, password: str, full_name: str) -> str:
        client = self._supabase_admin or self._get_supabase_admin_client()
        created = client.auth.admin.create_user(
            {
                "email": email,
                "password": password,
                "email_confirm": True,
                "user_metadata": {
                    "role": PORTFOLIO_MANAGER_ROLE,
                    "full_name": full_name,
                },
            }
        )
        user = created.user
        user_id = getattr(user, "id", None) or user.get("id")
        if not user_id:
            raise RuntimeError("Supabase did not return a user id")

        client.table("profiles").upsert(
            {
                "id": user_id,
                "email": email,
                "full_name": full_name,
                "role": PORTFOLIO_MANAGER_ROLE,
            }
        ).execute()
        return user_id

    @staticmethod
    def _get_supabase_admin_client() -> Client:
        settings = get_settings()
        if not settings.supabase_url or not settings.supabase_service_role_key:
            raise RuntimeError("Supabase admin credentials are not configured")
        return create_client(settings.supabase_url, settings.supabase_service_role_key)

    @staticmethod
    def _profile_to_dict(profile: UserProfile) -> dict[str, Any]:
        return {
            "id": profile.id,
            "email": profile.email,
            "full_name": profile.full_name,
            "role": profile.role,
            "created_at": profile.created_at.isoformat() if profile.created_at else None,
        }

    @staticmethod
    def _assignment_to_dict(assignment: PortfolioManagerAssignment) -> dict[str, Any]:
        return {
            "id": assignment.id,
            "project_id": assignment.project_id,
            "user_id": assignment.user_id,
            "assigned_by": assignment.assigned_by,
            "assigned_at": assignment.assigned_at.isoformat(),
            "user_email": assignment.user_email,
            "user_full_name": assignment.user_full_name,
        }
