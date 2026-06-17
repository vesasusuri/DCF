from abc import ABC, abstractmethod

from app.domain.entities.portfolio_manager import PortfolioManagerAssignment, UserProfile
from app.domain.entities.project import DashboardStats, Project, ProjectListResult
from app.domain.value_objects.project_filters import ProjectListFilters


class IProfileRepository(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: str) -> UserProfile | None: ...

    @abstractmethod
    async def get_by_email(self, email: str) -> UserProfile | None: ...

    @abstractmethod
    async def list_by_role(self, role: str) -> list[UserProfile]: ...


class IPortfolioManagerRepository(ABC):
    @abstractmethod
    async def get_assignment(self, project_id: str, user_id: str) -> PortfolioManagerAssignment | None: ...

    @abstractmethod
    async def list_by_project(self, project_id: str) -> list[PortfolioManagerAssignment]: ...

    @abstractmethod
    async def list_by_user(self, user_id: str) -> list[PortfolioManagerAssignment]: ...

    @abstractmethod
    async def create_assignment(
        self,
        project_id: str,
        user_id: str,
        assigned_by: str | None,
    ) -> PortfolioManagerAssignment: ...

    @abstractmethod
    async def update_assignment(
        self,
        project_id: str,
        user_id: str,
        assigned_by: str | None,
    ) -> PortfolioManagerAssignment: ...

    @abstractmethod
    async def delete_assignment(self, project_id: str, user_id: str) -> None: ...


class IAuditRepository(ABC):
    @abstractmethod
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
    ) -> None: ...


class IProjectRepository(ABC):
    @abstractmethod
    async def get_by_id(self, project_id: str) -> Project | None: ...

    @abstractmethod
    async def save(self, project: Project) -> Project: ...

    @abstractmethod
    async def list_by_organisation(self, org_id: str) -> list[Project]: ...

    @abstractmethod
    async def list_all(self, limit: int = 20) -> list[Project]: ...

    @abstractmethod
    async def list_summaries(self, filters: ProjectListFilters) -> ProjectListResult: ...

    @abstractmethod
    async def get_dashboard_stats(self) -> DashboardStats: ...
