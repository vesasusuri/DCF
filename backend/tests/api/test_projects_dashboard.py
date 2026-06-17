from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.dependencies import CurrentUser, get_dashboard_service, get_project_service, require_portfolio_manager
from app.domain.exceptions import InvalidProjectError, ProjectNotFoundError
from app.main import app

PM_USER = CurrentUser(
    id="pm-id",
    email="pm@example.com",
    full_name="Portfolio Manager",
    role="portfolio_manager",
)


@pytest.fixture
def mock_project_service():
    return AsyncMock()


@pytest.fixture
def mock_dashboard_service():
    return AsyncMock()


@pytest.fixture
async def pm_client(mock_project_service, mock_dashboard_service):
    app.dependency_overrides[require_portfolio_manager] = lambda: PM_USER
    app.dependency_overrides[get_project_service] = lambda: mock_project_service
    app.dependency_overrides[get_dashboard_service] = lambda: mock_dashboard_service
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_dashboard_stats_requires_auth():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/dashboard/stats")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_dashboard_stats_success(pm_client, mock_dashboard_service):
    mock_dashboard_service.get_stats.return_value = {
        "openProjects": 12,
        "assetsWithinScope": 318,
        "awaitingReview": 5,
        "reportsPerMonth": 9,
    }

    response = await pm_client.get(
        "/api/v1/dashboard/stats",
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 200
    assert response.json()["openProjects"] == 12


@pytest.mark.asyncio
async def test_list_projects_success(pm_client, mock_project_service):
    mock_project_service.list_projects.return_value = {
        "items": [
            {
                "id": "proj-1",
                "projectName": "LI Portfolio NRW",
                "clientName": "Colliers Germany",
                "assetCount": 47,
                "status": "active",
                "latestRun": None,
                "assignedTeam": "Team Rhein-Ruhr",
                "createdAt": "2026-01-01T00:00:00+00:00",
                "updatedAt": "2026-01-02T00:00:00+00:00",
            }
        ],
        "total": 1,
        "page": 1,
        "pages": 1,
    }

    response = await pm_client.get(
        "/api/v1/projects?status=active&search=logistics",
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 200
    mock_project_service.list_projects.assert_awaited_once_with(
        page=1,
        limit=20,
        status="active",
        search="logistics",
    )


@pytest.mark.asyncio
async def test_create_project_success(pm_client, mock_project_service):
    mock_project_service.create_project.return_value = {
        "id": "proj-1",
        "projectName": "New Project",
        "clientName": "Client GmbH",
        "currency": "EUR",
        "valuationDate": "2026-06-30",
        "reportingLanguage": "de",
        "status": "draft",
        "assignedTeam": None,
        "createdBy": "pm-id",
        "createdAt": "2026-06-17T00:00:00+00:00",
        "updatedAt": "2026-06-17T00:00:00+00:00",
        "metadata": {},
    }

    response = await pm_client.post(
        "/api/v1/projects",
        headers={"Authorization": "Bearer test-token"},
        json={
            "client": "Client GmbH",
            "projectName": "New Project",
            "currency": "EUR",
            "valuationDate": "2026-06-30",
            "reportingLanguage": "de",
        },
    )

    assert response.status_code == 201
    assert response.json()["projectName"] == "New Project"


@pytest.mark.asyncio
async def test_get_project_not_found(pm_client, mock_project_service):
    mock_project_service.get_project.side_effect = ProjectNotFoundError("missing")

    response = await pm_client.get(
        "/api/v1/projects/missing",
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_project_invalid_status(pm_client, mock_project_service):
    mock_project_service.update_project.side_effect = InvalidProjectError("Invalid project status: bogus")

    response = await pm_client.patch(
        "/api/v1/projects/proj-1",
        headers={"Authorization": "Bearer test-token"},
        json={"status": "bogus"},
    )

    assert response.status_code == 400
