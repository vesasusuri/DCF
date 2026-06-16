from collections.abc import AsyncGenerator
from dataclasses import dataclass

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from supabase import Client, create_client

from app.core.config import get_settings
from app.core.database import get_session
from app.domain.interfaces.file_storage import IFileStorage
from app.domain.interfaces.repositories import (
    IAuditRepository,
    IPortfolioManagerRepository,
    IProfileRepository,
    IProjectRepository,
)
from app.infrastructure.repositories.sql_audit_repository import SqlAuditRepository
from app.infrastructure.repositories.sql_portfolio_manager_repository import SqlPortfolioManagerRepository
from app.infrastructure.repositories.sql_profile_repository import SqlProfileRepository
from app.infrastructure.repositories.sql_project_repository import SqlProjectRepository
from app.infrastructure.storage.supabase_file_storage import SupabaseFileStorage
from app.services.audit_service import AuditService
from app.services.portfolio_manager_service import PortfolioManagerService
from app.services.project_service import ProjectService

security = HTTPBearer(auto_error=False)

ADMIN_ROLE = "admin"


@dataclass(frozen=True)
class CurrentUser:
    id: str
    email: str
    full_name: str | None
    role: str


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


async def get_profile_repo(
    session: AsyncSession = Depends(get_db_session),
) -> IProfileRepository:
    return SqlProfileRepository(session)


async def get_assignment_repo(
    session: AsyncSession = Depends(get_db_session),
) -> IPortfolioManagerRepository:
    return SqlPortfolioManagerRepository(session)


async def get_audit_repo(
    session: AsyncSession = Depends(get_db_session),
) -> IAuditRepository:
    return SqlAuditRepository(session)


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


def get_supabase_auth_client() -> Client:
    settings = get_settings()
    if not settings.supabase_url or not settings.supabase_anon_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Supabase auth is not configured.",
        )
    return create_client(settings.supabase_url, settings.supabase_anon_key)


def get_supabase_admin_client() -> Client:
    settings = get_settings()
    if not settings.supabase_url or not settings.supabase_service_role_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Supabase admin credentials are not configured.",
        )
    return create_client(settings.supabase_url, settings.supabase_service_role_key)


async def get_bearer_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> str:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header",
        )
    return credentials.credentials


async def get_current_user(
    token: str = Depends(get_bearer_token),
    profile_repo: IProfileRepository = Depends(get_profile_repo),
) -> CurrentUser:
    client = get_supabase_auth_client()
    try:
        response = client.auth.get_user(token)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
        ) from exc

    auth_user = response.user
    if auth_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
        )

    profile = await profile_repo.get_by_id(auth_user.id)
    if profile is None:
        metadata = auth_user.user_metadata or {}
        role = metadata.get("role", "user")
        return CurrentUser(
            id=auth_user.id,
            email=auth_user.email or "",
            full_name=metadata.get("full_name"),
            role=role,
        )

    return CurrentUser(
        id=profile.id,
        email=profile.email,
        full_name=profile.full_name,
        role=profile.role,
    )


async def require_admin(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    if current_user.role != ADMIN_ROLE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


async def get_audit_service(
    audit_repo: IAuditRepository = Depends(get_audit_repo),
) -> AuditService:
    return AuditService(audit_repo=audit_repo)


async def get_portfolio_manager_service(
    profile_repo: IProfileRepository = Depends(get_profile_repo),
    assignment_repo: IPortfolioManagerRepository = Depends(get_assignment_repo),
    project_repo: IProjectRepository = Depends(get_project_repo),
    audit_service: AuditService = Depends(get_audit_service),
) -> PortfolioManagerService:
    return PortfolioManagerService(
        profile_repo=profile_repo,
        assignment_repo=assignment_repo,
        project_repo=project_repo,
        audit_service=audit_service,
        supabase_admin=get_supabase_admin_client(),
    )
