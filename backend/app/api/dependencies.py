from collections.abc import AsyncGenerator

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_session
from app.domain.interfaces.file_storage import IFileStorage
from app.domain.interfaces.repositories import IProjectRepository
from app.infrastructure.repositories.sql_project_repository import SqlProjectRepository
from app.infrastructure.storage.supabase_file_storage import SupabaseFileStorage
from app.services.project_service import ProjectService


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    settings = get_settings()
    if not settings.database_url:
        raise HTTPException(
            status_code=503,
            detail="DATABASE_URL is not configured.",
        )
    async for session in get_session():
        yield session


async def get_project_repo(
    session: AsyncSession = Depends(get_db_session),
) -> IProjectRepository:
    return SqlProjectRepository(session)


async def get_project_service(
    project_repo: IProjectRepository = Depends(get_project_repo),
) -> ProjectService:
    return ProjectService(project_repo=project_repo)


async def get_file_storage() -> IFileStorage:
    settings = get_settings()
    if not settings.supabase_url or not settings.supabase_service_role_key:
        raise HTTPException(
            status_code=503,
            detail="Supabase is not configured. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY.",
        )
    return SupabaseFileStorage()
