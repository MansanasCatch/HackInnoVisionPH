"""Dependency-injection wiring: builds services for each request."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.db.session import get_db
from app.repositories.device_repository import SqlAlchemyDeviceRepository
from app.repositories.onboarding_repository import SqlAlchemyOnboardingRepository
from app.services.device_service import DeviceService
from app.services.health_service import HealthService
from app.services.local_ai_service import LocalAIService
from app.services.onboarding_service import OnboardingService

DbSession = Annotated[Session, Depends(get_db)]
AppSettings = Annotated[Settings, Depends(get_settings)]


def get_onboarding_service(db: DbSession) -> OnboardingService:
    """Compose an :class:`OnboardingService` backed by SQLAlchemy."""
    return OnboardingService(SqlAlchemyOnboardingRepository(db))


def get_device_service(db: DbSession) -> DeviceService:
    """Compose a :class:`DeviceService` backed by SQLAlchemy."""
    return DeviceService(
        device_repository=SqlAlchemyDeviceRepository(db),
        onboarding_repository=SqlAlchemyOnboardingRepository(db),
    )


def get_local_ai_service(db: DbSession) -> LocalAIService:
    """Compose a :class:`LocalAIService` backed by SQLAlchemy DeviceRepository."""
    return LocalAIService(device_repository=SqlAlchemyDeviceRepository(db))


def get_health_service(db: DbSession, settings: AppSettings) -> HealthService:
    """Compose a :class:`HealthService`."""
    return HealthService(db, settings)


OnboardingServiceDep = Annotated[OnboardingService, Depends(get_onboarding_service)]
DeviceServiceDep = Annotated[DeviceService, Depends(get_device_service)]
LocalAIServiceDep = Annotated[LocalAIService, Depends(get_local_ai_service)]
HealthServiceDep = Annotated[HealthService, Depends(get_health_service)]
