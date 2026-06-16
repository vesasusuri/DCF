from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_project_service
from app.domain.exceptions import DomainError, ProjectNotFoundError
from app.services.project_service import ProjectService

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("")
async def list_projects(
    service: ProjectService = Depends(get_project_service),
) -> dict:
    try:
        data = await service.list_projects()
        return {"data": data}
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except DomainError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/{project_id}")
async def get_project(
    project_id: str,
    service: ProjectService = Depends(get_project_service),
) -> dict:
    try:
        data = await service.get_project(project_id)
        return {"data": data}
    except ProjectNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
