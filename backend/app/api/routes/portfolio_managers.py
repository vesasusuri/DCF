from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import CurrentUser, get_portfolio_manager_service, require_admin
from app.api.schemas.portfolio_managers import (
    AssignPortfolioManagerRequest,
    CreatePortfolioManagerRequest,
)
from app.domain.exceptions import (
    AssignmentNotFoundError,
    DomainError,
    DuplicateAssignmentError,
    NotPortfolioManagerError,
    ProjectNotFoundError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from app.services.portfolio_manager_service import PortfolioManagerService

router = APIRouter(tags=["portfolio-managers"])


def _handle_domain_error(exc: DomainError) -> HTTPException:
    if isinstance(exc, ProjectNotFoundError):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    if isinstance(exc, (UserNotFoundError, AssignmentNotFoundError)):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    if isinstance(exc, UserAlreadyExistsError):
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    if isinstance(exc, DuplicateAssignmentError):
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    if isinstance(exc, NotPortfolioManagerError):
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.post("/portfolio-managers")
async def create_portfolio_manager(
    body: CreatePortfolioManagerRequest,
    admin: CurrentUser = Depends(require_admin),
    service: PortfolioManagerService = Depends(get_portfolio_manager_service),
) -> dict:
    try:
        data = await service.create_portfolio_manager(
            email=body.email,
            password=body.password,
            full_name=body.full_name,
            actor_id=admin.id,
        )
        return {"data": data}
    except DomainError as exc:
        raise _handle_domain_error(exc) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc


@router.get("/portfolio-managers")
async def list_portfolio_managers(
    _: CurrentUser = Depends(require_admin),
    service: PortfolioManagerService = Depends(get_portfolio_manager_service),
) -> dict:
    data = await service.list_portfolio_managers()
    return {"data": data}


@router.get("/projects/{project_id}/portfolio-managers")
async def list_project_portfolio_managers(
    project_id: str,
    _: CurrentUser = Depends(require_admin),
    service: PortfolioManagerService = Depends(get_portfolio_manager_service),
) -> dict:
    try:
        data = await service.list_project_assignments(project_id)
        return {"data": data}
    except DomainError as exc:
        raise _handle_domain_error(exc) from exc


@router.post("/projects/{project_id}/portfolio-managers")
async def assign_portfolio_manager(
    project_id: str,
    body: AssignPortfolioManagerRequest,
    admin: CurrentUser = Depends(require_admin),
    service: PortfolioManagerService = Depends(get_portfolio_manager_service),
) -> dict:
    try:
        data = await service.assign_to_project(
            project_id=project_id,
            user_id=body.user_id,
            actor_id=admin.id,
        )
        return {"data": data}
    except DomainError as exc:
        raise _handle_domain_error(exc) from exc


@router.put("/projects/{project_id}/portfolio-managers/{user_id}")
async def update_portfolio_manager_assignment(
    project_id: str,
    user_id: str,
    admin: CurrentUser = Depends(require_admin),
    service: PortfolioManagerService = Depends(get_portfolio_manager_service),
) -> dict:
    try:
        data = await service.update_assignment(
            project_id=project_id,
            user_id=user_id,
            actor_id=admin.id,
        )
        return {"data": data}
    except DomainError as exc:
        raise _handle_domain_error(exc) from exc


@router.delete("/projects/{project_id}/portfolio-managers/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_portfolio_manager_assignment(
    project_id: str,
    user_id: str,
    admin: CurrentUser = Depends(require_admin),
    service: PortfolioManagerService = Depends(get_portfolio_manager_service),
) -> None:
    try:
        await service.remove_assignment(
            project_id=project_id,
            user_id=user_id,
            actor_id=admin.id,
        )
    except DomainError as exc:
        raise _handle_domain_error(exc) from exc
