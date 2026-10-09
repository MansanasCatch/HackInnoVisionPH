"""CRUD endpoints for hackathon projects."""

from typing import Annotated

from fastapi import APIRouter, Query, status

from app.api.deps import ProjectServiceDep
from app.models.project import ProjectStatus
from app.schemas.project import ProjectCreate, ProjectRead, ProjectStats

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("", response_model=list[ProjectRead], summary="List projects")
def list_projects(
    service: ProjectServiceDep,
    status_filter: Annotated[ProjectStatus | None, Query(alias="status")] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[ProjectRead]:
    """Return projects, newest first."""
    return service.list_projects(status=status_filter, limit=limit, offset=offset)


@router.get("/stats", response_model=ProjectStats, summary="Project statistics")
def get_project_stats(service: ProjectServiceDep) -> ProjectStats:
    """Return project counts grouped by status."""
    return service.get_stats()


@router.get("/{project_id}", response_model=ProjectRead, summary="Get a project")
def get_project(project_id: int, service: ProjectServiceDep) -> ProjectRead:
    """Return a single project by id."""
    return service.get_project(project_id)


@router.post(
    "",
    response_model=ProjectRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register a project",
)
def create_project(payload: ProjectCreate, service: ProjectServiceDep) -> ProjectRead:
    """Create a new hackathon project."""
    return service.create_project(payload)
