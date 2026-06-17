import pytest
from datetime import date

from app.domain.constants import PROJECT_STATUS_DRAFT
from app.domain.entities.project import Project
from app.domain.exceptions import InvalidProjectError
from app.services.project_service import ProjectService


class FakeProjectRepo:
    def __init__(self):
        self.saved = None

    async def list_summaries(self, filters):
        from app.domain.entities.project import ProjectListResult

        return ProjectListResult(items=[], total=0)

    async def get_by_id(self, project_id: str):
        return None

    async def save(self, project: Project):
        self.saved = project
        project.id = "generated-id"
        return project


@pytest.mark.asyncio
async def test_create_project_sets_draft_status():
    repo = FakeProjectRepo()
    service = ProjectService(repo)

    result = await service.create_project(
        client="Client GmbH",
        project_name="Test Project",
        currency="eur",
        valuation_date=date(2026, 6, 30),
        reporting_language="de",
        created_by="user-1",
    )

    assert result["status"] == PROJECT_STATUS_DRAFT
    assert repo.saved.currency == "EUR"


@pytest.mark.asyncio
async def test_invalid_status_filter_raises():
    repo = FakeProjectRepo()
    service = ProjectService(repo)

    with pytest.raises(InvalidProjectError):
        await service.list_projects(status="bogus")
