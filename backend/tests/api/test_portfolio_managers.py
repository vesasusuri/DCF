from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.dependencies import CurrentUser, get_portfolio_manager_service, require_admin
from app.domain.exceptions import (
    AssignmentNotFoundError,
    DuplicateAssignmentError,
    NotPortfolioManagerError,
    ProjectNotFoundError,
    UserAlreadyExistsError,
)
from app.main import app

ADMIN_USER = CurrentUser(
    id="admin-id",
    email="admin@example.com",
    full_name="System Admin",
    role="admin",
)


@pytest.fixture
def mock_service():
    return AsyncMock()


@pytest.fixture
async def admin_client(mock_service):
    app.dependency_overrides[require_admin] = lambda: ADMIN_USER
    app.dependency_overrides[get_portfolio_manager_service] = lambda: mock_service
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_list_portfolio_managers_requires_auth():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/portfolio-managers")
    assert response.status_code == 401
    assert "authorization" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_list_portfolio_managers_success(admin_client, mock_service):
    mock_service.list_portfolio_managers.return_value = [
        {
            "id": "pm-1",
            "email": "pm@example.com",
            "full_name": "Portfolio Manager",
            "role": "portfolio_manager",
            "created_at": "2026-01-01T00:00:00+00:00",
        }
    ]

    response = await admin_client.get(
        "/api/v1/portfolio-managers",
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 200
    assert response.json()["data"][0]["email"] == "pm@example.com"


@pytest.mark.asyncio
async def test_create_portfolio_manager_success(admin_client, mock_service):
    mock_service.create_portfolio_manager.return_value = {
        "id": "pm-1",
        "email": "new-pm@example.com",
        "full_name": "New PM",
        "role": "portfolio_manager",
        "created_at": "2026-01-01T00:00:00+00:00",
    }

    response = await admin_client.post(
        "/api/v1/portfolio-managers",
        headers={"Authorization": "Bearer test-token"},
        json={
            "email": "new-pm@example.com",
            "password": "SecurePass1",
            "full_name": "New PM",
        },
    )

    assert response.status_code == 200
    mock_service.create_portfolio_manager.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_portfolio_manager_conflict(admin_client, mock_service):
    mock_service.create_portfolio_manager.side_effect = UserAlreadyExistsError("new-pm@example.com")

    response = await admin_client.post(
        "/api/v1/portfolio-managers",
        headers={"Authorization": "Bearer test-token"},
        json={
            "email": "new-pm@example.com",
            "password": "SecurePass1",
            "full_name": "New PM",
        },
    )

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_assign_portfolio_manager_success(admin_client, mock_service):
    mock_service.assign_to_project.return_value = {
        "id": "assignment-1",
        "project_id": "project-1",
        "user_id": "pm-1",
        "assigned_by": ADMIN_USER.id,
        "assigned_at": datetime.now(UTC).isoformat(),
        "user_email": "pm@example.com",
        "user_full_name": "Portfolio Manager",
    }

    response = await admin_client.post(
        "/api/v1/projects/project-1/portfolio-managers",
        headers={"Authorization": "Bearer test-token"},
        json={"user_id": "pm-1"},
    )

    assert response.status_code == 200
    assert response.json()["data"]["project_id"] == "project-1"


@pytest.mark.asyncio
async def test_assign_portfolio_manager_duplicate(admin_client, mock_service):
    mock_service.assign_to_project.side_effect = DuplicateAssignmentError("project-1", "pm-1")

    response = await admin_client.post(
        "/api/v1/projects/project-1/portfolio-managers",
        headers={"Authorization": "Bearer test-token"},
        json={"user_id": "pm-1"},
    )

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_assign_portfolio_manager_invalid_role(admin_client, mock_service):
    mock_service.assign_to_project.side_effect = NotPortfolioManagerError("user-1")

    response = await admin_client.post(
        "/api/v1/projects/project-1/portfolio-managers",
        headers={"Authorization": "Bearer test-token"},
        json={"user_id": "user-1"},
    )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_assign_portfolio_manager_project_not_found(admin_client, mock_service):
    mock_service.assign_to_project.side_effect = ProjectNotFoundError("missing-project")

    response = await admin_client.post(
        "/api/v1/projects/missing-project/portfolio-managers",
        headers={"Authorization": "Bearer test-token"},
        json={"user_id": "pm-1"},
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_remove_portfolio_manager_success(admin_client, mock_service):
    response = await admin_client.delete(
        "/api/v1/projects/project-1/portfolio-managers/pm-1",
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 204
    mock_service.remove_assignment.assert_awaited_once()


@pytest.mark.asyncio
async def test_remove_portfolio_manager_not_found(admin_client, mock_service):
    mock_service.remove_assignment.side_effect = AssignmentNotFoundError("project-1", "pm-1")

    response = await admin_client.delete(
        "/api/v1/projects/project-1/portfolio-managers/pm-1",
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 404
