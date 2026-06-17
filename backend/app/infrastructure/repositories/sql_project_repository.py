from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import func, lateral, or_, select, true
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.constants import (
    AWAITING_REVIEW_PROJECT_STATUSES,
    AWAITING_REVIEW_RUN_STATUSES,
    NON_ARCHIVED_STATUSES,
    PROJECT_STATUS_ARCHIVED,
)
from app.domain.entities.project import DashboardStats, LatestRunInfo, Project, ProjectListResult, ProjectSummary
from app.domain.interfaces.repositories import IProjectRepository
from app.domain.value_objects.project_filters import ProjectListFilters
from app.infrastructure.models.project_model import (
    DcfModel,
    ProjectAssetModel,
    ProjectReportModel,
    ValuationRunModel,
)


class SqlProjectRepository(IProjectRepository):
    """Transitional repository using dcf_models table until full schema migration."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, project_id: str) -> Project | None:
        result = await self._session.get(DcfModel, project_id)
        return self._to_domain(result) if result else None

    async def save(self, project: Project) -> Project:
        if project.id:
            model = await self._session.get(DcfModel, project.id)
            if model is None:
                model = DcfModel(id=UUID(project.id))
                self._session.add(model)
        else:
            new_id = uuid4()
            project.id = str(new_id)
            model = DcfModel(id=new_id)
            self._session.add(model)

        model.name = project.name
        model.client = project.client
        model.currency = project.currency
        model.valuation_date = project.valuation_date
        model.reporting_language = project.reporting_language
        model.status = project.status
        model.team_name = project.team_name
        model.created_by = UUID(project.created_by) if project.created_by else None
        model.ticker = project.metadata.get("ticker")
        if "assumptions" in project.metadata:
            model.assumptions = project.metadata["assumptions"]

        await self._session.flush()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def list_by_organisation(self, org_id: str) -> list[Project]:
        return await self.list_all()

    async def list_all(self, limit: int = 20) -> list[Project]:
        stmt = select(DcfModel).order_by(DcfModel.updated_at.desc()).limit(limit)
        result = await self._session.execute(stmt)
        return [self._to_domain(row) for row in result.scalars().all()]

    async def list_summaries(self, filters: ProjectListFilters) -> ProjectListResult:
        asset_count = (
            select(func.count(ProjectAssetModel.id))
            .where(ProjectAssetModel.project_id == DcfModel.id)
            .correlate(DcfModel)
            .scalar_subquery()
        )

        latest_run_lateral = lateral(
            select(
                ValuationRunModel.run_number.label("run_number"),
                ValuationRunModel.status.label("run_status"),
                ValuationRunModel.completed_at.label("run_completed_at"),
                ValuationRunModel.created_at.label("run_created_at"),
            )
            .where(ValuationRunModel.project_id == DcfModel.id)
            .order_by(ValuationRunModel.created_at.desc())
            .limit(1)
        ).alias("latest_run")

        conditions = self._build_filter_conditions(filters)
        count_stmt = select(func.count()).select_from(DcfModel)
        if conditions:
            count_stmt = count_stmt.where(*conditions)
        total = int(await self._session.scalar(count_stmt) or 0)

        page = max(filters.page, 1)
        limit = min(max(filters.limit, 1), 100)
        offset = (page - 1) * limit

        stmt = (
            select(
                DcfModel,
                asset_count.label("asset_count"),
                latest_run_lateral.c.run_number,
                latest_run_lateral.c.run_status,
                latest_run_lateral.c.run_completed_at,
                latest_run_lateral.c.run_created_at,
            )
            .select_from(DcfModel)
            .outerjoin(latest_run_lateral, true())
        )
        if conditions:
            stmt = stmt.where(*conditions)
        stmt = stmt.order_by(DcfModel.updated_at.desc()).offset(offset).limit(limit)

        result = await self._session.execute(stmt)
        items = [self._to_summary(row) for row in result.all()]
        return ProjectListResult(items=items, total=total)

    async def get_dashboard_stats(self) -> DashboardStats:
        now = datetime.now(UTC)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        open_projects_stmt = (
            select(func.count())
            .select_from(DcfModel)
            .where(DcfModel.status.in_(NON_ARCHIVED_STATUSES))
        )
        assets_stmt = select(func.count()).select_from(ProjectAssetModel)

        awaiting_projects_stmt = (
            select(func.count())
            .select_from(DcfModel)
            .where(DcfModel.status.in_(AWAITING_REVIEW_PROJECT_STATUSES))
        )
        awaiting_runs_stmt = (
            select(func.count())
            .select_from(ValuationRunModel)
            .where(ValuationRunModel.status.in_(AWAITING_REVIEW_RUN_STATUSES))
        )
        reports_stmt = (
            select(func.count())
            .select_from(ProjectReportModel)
            .where(ProjectReportModel.generated_at >= month_start)
        )

        open_projects = int(await self._session.scalar(open_projects_stmt) or 0)
        assets_within_scope = int(await self._session.scalar(assets_stmt) or 0)
        awaiting_projects = int(await self._session.scalar(awaiting_projects_stmt) or 0)
        awaiting_runs = int(await self._session.scalar(awaiting_runs_stmt) or 0)
        reports_per_month = int(await self._session.scalar(reports_stmt) or 0)

        return DashboardStats(
            open_projects=open_projects,
            assets_within_scope=assets_within_scope,
            awaiting_review=awaiting_projects + awaiting_runs,
            reports_per_month=reports_per_month,
        )

    def _build_filter_conditions(self, filters: ProjectListFilters) -> list:
        conditions = []

        if filters.status == "archived":
            conditions.append(DcfModel.status == PROJECT_STATUS_ARCHIVED)
        elif filters.status == "active":
            conditions.append(DcfModel.status.in_(NON_ARCHIVED_STATUSES))

        if filters.search:
            term = f"%{filters.search.strip()}%"
            conditions.append(
                or_(
                    DcfModel.name.ilike(term),
                    DcfModel.client.ilike(term),
                )
            )

        return conditions

    @staticmethod
    def _to_domain(model: DcfModel) -> Project:
        metadata: dict = {"assumptions": model.assumptions}
        if model.ticker:
            metadata["ticker"] = model.ticker
        return Project(
            id=str(model.id),
            name=model.name,
            client=model.client,
            currency=model.currency,
            valuation_date=model.valuation_date,
            reporting_language=model.reporting_language,
            status=model.status,
            team_name=model.team_name,
            created_by=str(model.created_by) if model.created_by else None,
            created_at=model.created_at,
            updated_at=model.updated_at,
            metadata=metadata,
        )

    @staticmethod
    def _to_summary(row) -> ProjectSummary:
        model, asset_count, run_number, run_status, run_completed_at, run_created_at = row
        latest_run = None
        if run_number is not None:
            latest_run = LatestRunInfo(
                run_number=run_number,
                status=run_status,
                completed_at=run_completed_at,
                created_at=run_created_at,
            )
        return ProjectSummary(
            id=str(model.id),
            name=model.name,
            client=model.client,
            asset_count=int(asset_count or 0),
            status=model.status,
            latest_run=latest_run,
            team_name=model.team_name,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
