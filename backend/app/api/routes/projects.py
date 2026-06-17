from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import (
    CurrentUser,
    get_project_service,
    require_portfolio_manager,
)
from app.api.schemas.projects import (
    CreateProjectRequest,
    UpdateProjectRequest,
)
from app.domain.exceptions import DomainError, InvalidProjectError, ProjectNotFoundError
from app.services.project_service import ProjectService

router = APIRouter(prefix="/projects", tags=["projects"])


def _handle_domain_error(exc: DomainError) -> HTTPException:
    if isinstance(exc, ProjectNotFoundError):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    if isinstance(exc, InvalidProjectError):
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get("")
async def list_projects(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: str | None = Query(None),
    search: str | None = Query(None),
    _: CurrentUser = Depends(require_portfolio_manager),
    service: ProjectService = Depends(get_project_service),
) -> dict:
    try:
        return await service.list_projects(
            page=page,
            limit=limit,
            status=status,
            search=search,
        )
    except DomainError as exc:
        raise _handle_domain_error(exc) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc


@router.get("/{project_id}")
async def get_project(
    project_id: str,
    _: CurrentUser = Depends(require_portfolio_manager),
    service: ProjectService = Depends(get_project_service),
) -> dict:
    try:
        return await service.get_project(project_id)
    except ProjectNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_project(
    body: CreateProjectRequest,
    current_user: CurrentUser = Depends(require_portfolio_manager),
    service: ProjectService = Depends(get_project_service),
) -> dict:
    try:
        return await service.create_project(
            client=body.client,
            project_name=body.project_name,
            currency=body.currency,
            valuation_date=body.valuation_date,
            reporting_language=body.reporting_language,
            created_by=current_user.id,
        )
    except DomainError as exc:
        raise _handle_domain_error(exc) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc


@router.patch("/{project_id}")
async def update_project(
    project_id: str,
    body: UpdateProjectRequest,
    _: CurrentUser = Depends(require_portfolio_manager),
    service: ProjectService = Depends(get_project_service),
) -> dict:
    updates = body.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No changes provided.")
    try:
        return await service.update_project(project_id, updates)
    except DomainError as exc:
        raise _handle_domain_error(exc) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
