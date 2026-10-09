"""Dependency-injection wiring: builds services for each request."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.db.session import get_db
from app.repositories.onboarding_repository import SqlAlchemyOnboardingRepository
from app.services.health_service import HealthService
from app.services.onboarding_service import OnboardingService

DbSession = Annotated[Session, Depends(get_db)]
AppSettings = Annotated[Settings, Depends(get_settings)]


def get_onboarding_service(db: DbSession) -> OnboardingService:
    """Compose an :class:`OnboardingService` backed by SQLAlchemy."""
    return OnboardingService(SqlAlchemyOnboardingRepository(db))


def get_health_service(db: DbSession, settings: AppSettings) -> HealthService:
    """Compose a :class:`HealthService`."""
    return HealthService(db, settings)


OnboardingServiceDep = Annotated[OnboardingService, Depends(get_onboarding_service)]
HealthServiceDep = Annotated[HealthService, Depends(get_health_service)]
