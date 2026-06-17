from fastapi import APIRouter, Depends

from app.api.dependencies import CurrentUser, get_dashboard_service, require_portfolio_manager
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats")
async def get_dashboard_stats(
    _: CurrentUser = Depends(require_portfolio_manager),
    service: DashboardService = Depends(get_dashboard_service),
) -> dict:
    return await service.get_stats()
