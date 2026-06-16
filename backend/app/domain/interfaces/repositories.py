from abc import ABC, abstractmethod

from app.domain.entities.project import Project


class IProjectRepository(ABC):
    @abstractmethod
    async def get_by_id(self, project_id: str) -> Project | None: ...

    @abstractmethod
    async def save(self, project: Project) -> None: ...

    @abstractmethod
    async def list_by_organisation(self, org_id: str) -> list[Project]: ...

    @abstractmethod
    async def list_all(self, limit: int = 20) -> list[Project]: ...
