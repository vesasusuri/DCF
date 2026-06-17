from pydantic import BaseModel, ConfigDict, Field


class DashboardStatsResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    open_projects: int = Field(serialization_alias="openProjects")
    assets_within_scope: int = Field(serialization_alias="assetsWithinScope")
    awaiting_review: int = Field(serialization_alias="awaitingReview")
    reports_per_month: int = Field(serialization_alias="reportsPerMonth")
