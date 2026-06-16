from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.domain.exceptions import (
    AssignmentNotFoundError,
    DuplicateAssignmentError,
    NotPortfolioManagerError,
    ProjectNotFoundError,
    UserNotFoundError,
)
from app.domain.entities.portfolio_manager import PortfolioManagerAssignment, UserProfile
from app.domain.entities.project import Project
from app.services.audit_service import AuditService
from app.services.portfolio_manager_service import PortfolioManagerService


@pytest.fixture
def service_deps():
    profile_repo = AsyncMock()
    assignment_repo = AsyncMock()
    project_repo = AsyncMock()
    audit_service = AsyncMock(spec=AuditService)
    return profile_repo, assignment_repo, project_repo, audit_service


@pytest.fixture
def service(service_deps):
    profile_repo, assignment_repo, project_repo, audit_service = service_deps
    return PortfolioManagerService(
        profile_repo=profile_repo,
        assignment_repo=assignment_repo,
        project_repo=project_repo,
        audit_service=audit_service,
        supabase_admin=MagicMock(),
    )


@pytest.mark.asyncio
async def test_assign_to_project_success(service, service_deps):
    profile_repo, assignment_repo, project_repo, audit_service = service_deps
    project_repo.get_by_id.return_value = Project(id="project-1", name="Test Project")
    profile_repo.get_by_id.return_value = UserProfile(
        id="pm-1",
        email="pm@example.com",
        full_name="PM",
        role="portfolio_manager",
    )
    assignment_repo.get_assignment.return_value = None
    assignment_repo.create_assignment.return_value = PortfolioManagerAssignment(
        id="assignment-1",
        project_id="project-1",
        user_id="pm-1",
        assigned_by="admin-1",
        assigned_at=datetime.now(UTC),
        user_email="pm@example.com",
        user_full_name="PM",
    )

    result = await service.assign_to_project(
        project_id="project-1",
        user_id="pm-1",
        actor_id="admin-1",
    )

    assert result["user_id"] == "pm-1"
    audit_service.record_assignment_created.assert_awaited_once()


@pytest.mark.asyncio
async def test_assign_to_project_rejects_non_manager(service, service_deps):
    _, _, project_repo, _ = service_deps
    project_repo.get_by_id.return_value = Project(id="project-1", name="Test Project")
    service_deps[0].get_by_id.return_value = UserProfile(
        id="user-1",
        email="user@example.com",
        full_name="User",
        role="user",
    )

    with pytest.raises(NotPortfolioManagerError):
        await service.assign_to_project(
            project_id="project-1",
            user_id="user-1",
            actor_id="admin-1",
        )


@pytest.mark.asyncio
async def test_assign_to_project_rejects_duplicate(service, service_deps):
    _, assignment_repo, project_repo, _ = service_deps
    project_repo.get_by_id.return_value = Project(id="project-1", name="Test Project")
    service_deps[0].get_by_id.return_value = UserProfile(
        id="pm-1",
        email="pm@example.com",
        full_name="PM",
        role="portfolio_manager",
    )
    assignment_repo.get_assignment.return_value = PortfolioManagerAssignment(
        id="assignment-1",
        project_id="project-1",
        user_id="pm-1",
        assigned_by="admin-1",
        assigned_at=datetime.now(UTC),
    )

    with pytest.raises(DuplicateAssignmentError):
        await service.assign_to_project(
            project_id="project-1",
            user_id="pm-1",
            actor_id="admin-1",
        )


@pytest.mark.asyncio
async def test_assign_to_project_rejects_missing_project(service, service_deps):
    service_deps[2].get_by_id.return_value = None

    with pytest.raises(ProjectNotFoundError):
        await service.assign_to_project(
            project_id="missing",
            user_id="pm-1",
            actor_id="admin-1",
        )


@pytest.mark.asyncio
async def test_remove_assignment_not_found(service, service_deps):
    _, assignment_repo, project_repo, _ = service_deps
    project_repo.get_by_id.return_value = Project(id="project-1", name="Test Project")
    assignment_repo.get_assignment.return_value = None

    with pytest.raises(AssignmentNotFoundError):
        await service.remove_assignment(
            project_id="project-1",
            user_id="pm-1",
            actor_id="admin-1",
        )


@pytest.mark.asyncio
async def test_remove_assignment_success(service, service_deps):
    _, assignment_repo, project_repo, audit_service = service_deps
    project_repo.get_by_id.return_value = Project(id="project-1", name="Test Project")
    assignment_repo.get_assignment.return_value = PortfolioManagerAssignment(
        id="assignment-1",
        project_id="project-1",
        user_id="pm-1",
        assigned_by="admin-1",
        assigned_at=datetime.now(UTC),
        user_email="pm@example.com",
        user_full_name="PM",
    )

    await service.remove_assignment(
        project_id="project-1",
        user_id="pm-1",
        actor_id="admin-1",
    )

    assignment_repo.delete_assignment.assert_awaited_once_with("project-1", "pm-1")
    audit_service.record_assignment_removed.assert_awaited_once()
