"""Dependency-injection wiring: builds services for each request."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.db.session import get_db
from app.repositories.project_repository import SqlAlchemyProjectRepository
from app.services.health_service import HealthService
from app.services.project_service import ProjectService

DbSession = Annotated[Session, Depends(get_db)]
AppSettings = Annotated[Settings, Depends(get_settings)]


def get_project_service(db: DbSession) -> ProjectService:
    """Compose a :class:`ProjectService` backed by SQLAlchemy."""
    return ProjectService(SqlAlchemyProjectRepository(db))


def get_health_service(db: DbSession, settings: AppSettings) -> HealthService:
    """Compose a :class:`HealthService`."""
    return HealthService(db, settings)


ProjectServiceDep = Annotated[ProjectService, Depends(get_project_service)]
HealthServiceDep = Annotated[HealthService, Depends(get_health_service)]
