"""Use cases for managing hackathon projects."""

from app.core.exceptions import ConflictError, NotFoundError
from app.core.logging import get_logger
from app.models.project import Project, ProjectStatus
from app.repositories.project_repository import AbstractProjectRepository
from app.schemas.project import ProjectCreate, ProjectRead, ProjectStats

logger = get_logger(__name__)


class ProjectService:
    """Application service for the ``Project`` aggregate.

    Depends only on the repository abstraction, which keeps it trivially
    unit-testable and independent of FastAPI / SQLAlchemy.
    """

    def __init__(self, repository: AbstractProjectRepository) -> None:
        self._repository = repository

    def list_projects(
        self, *, status: ProjectStatus | None = None, limit: int = 50, offset: int = 0
    ) -> list[ProjectRead]:
        status_value = status.value if status else None
        projects = self._repository.list(status=status_value, limit=limit, offset=offset)
        return [ProjectRead.model_validate(project) for project in projects]

    def get_project(self, project_id: int) -> ProjectRead:
        return ProjectRead.model_validate(self._get_or_raise(project_id))

    def create_project(self, payload: ProjectCreate) -> ProjectRead:
        self._ensure_name_available(payload.name)
        data = payload.model_dump()
        data["status"] = payload.status.value
        project = self._repository.add(Project(**data))
        logger.info("Project created: id=%s name=%s", project.id, project.name)
        return ProjectRead.model_validate(project)

    def get_stats(self) -> ProjectStats:
        counts = self._repository.count_by_status()
        by_status = {status: counts.get(status.value, 0) for status in ProjectStatus}
        return ProjectStats(total=sum(by_status.values()), by_status=by_status)

    def _get_or_raise(self, project_id: int) -> Project:
        project = self._repository.get(project_id)
        if project is None:
            raise NotFoundError(f"Project with id {project_id} was not found.")
        return project

    def _ensure_name_available(self, name: str) -> None:
        if self._repository.get_by_name(name) is not None:
            raise ConflictError(f"A project named '{name}' already exists.")
