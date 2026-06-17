from datetime import date
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class LatestRunResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    run_number: int | None = Field(None, serialization_alias="runNumber")
    status: str | None = None
    completed_at: str | None = Field(None, serialization_alias="completedAt")
    created_at: str | None = Field(None, serialization_alias="createdAt")


class ProjectSummaryResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    project_name: str = Field(serialization_alias="projectName")
    client_name: str | None = Field(None, serialization_alias="clientName")
    asset_count: int = Field(serialization_alias="assetCount")
    status: str
    latest_run: LatestRunResponse | None = Field(None, serialization_alias="latestRun")
    assigned_team: str | None = Field(None, serialization_alias="assignedTeam")
    created_at: str | None = Field(None, serialization_alias="createdAt")
    updated_at: str | None = Field(None, serialization_alias="updatedAt")


class ProjectListResponse(BaseModel):
    items: list[ProjectSummaryResponse]
    total: int
    page: int
    pages: int


class ProjectDetailResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    project_name: str = Field(serialization_alias="projectName")
    client_name: str | None = Field(None, serialization_alias="clientName")
    currency: str
    valuation_date: str | None = Field(None, serialization_alias="valuationDate")
    reporting_language: str = Field(serialization_alias="reportingLanguage")
    status: str
    assigned_team: str | None = Field(None, serialization_alias="assignedTeam")
    created_by: str | None = Field(None, serialization_alias="createdBy")
    created_at: str | None = Field(None, serialization_alias="createdAt")
    updated_at: str | None = Field(None, serialization_alias="updatedAt")
    metadata: dict[str, Any] = Field(default_factory=dict)


class CreateProjectRequest(BaseModel):
    client: str = Field(min_length=1, max_length=255)
    project_name: str = Field(min_length=1, max_length=255, alias="projectName")
    currency: str = Field(min_length=3, max_length=3)
    valuation_date: date = Field(alias="valuationDate")
    reporting_language: str = Field(min_length=2, max_length=10, alias="reportingLanguage")

    model_config = ConfigDict(populate_by_name=True)


class UpdateProjectRequest(BaseModel):
    project_name: str | None = Field(None, min_length=1, max_length=255, alias="projectName")
    client: str | None = Field(None, min_length=1, max_length=255)
    currency: str | None = Field(None, min_length=3, max_length=3)
    valuation_date: date | None = Field(None, alias="valuationDate")
    reporting_language: str | None = Field(None, min_length=2, max_length=10, alias="reportingLanguage")
    status: str | None = None
    assigned_team: str | None = Field(None, max_length=255, alias="assignedTeam")

    model_config = ConfigDict(populate_by_name=True)
