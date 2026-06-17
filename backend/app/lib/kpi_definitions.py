"""KPI registry — single source of truth for dashboard metrics."""

KPI_REGISTRY: dict[str, dict] = {
    "openProjects": {
        "description": "Count of non-archived projects",
        "source": "dcf_models.status",
    },
    "assetsWithinScope": {
        "description": "Count of assets linked to projects",
        "source": "project_assets",
    },
    "awaitingReview": {
        "description": "Projects in test status plus valuation runs pending review",
        "source": "dcf_models.status, valuation_runs.status",
    },
    "reportsPerMonth": {
        "description": "Reports generated in the current calendar month",
        "source": "project_reports.generated_at",
    },
}
