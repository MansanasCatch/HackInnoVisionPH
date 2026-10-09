"""Dependency-injection wiring: builds services for each request."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.db.session import get_db
from app.repositories.device_repository import SqlAlchemyDeviceRepository
from app.repositories.learning_resource_repository import SqlAlchemyLearningResourceRepository
from app.repositories.onboarding_repository import SqlAlchemyOnboardingRepository
from app.repositories.study_repository import SqlAlchemyStudyRepository
from app.services.device_service import DeviceService
from app.services.health_service import HealthService
from app.services.learning_resource_service import LearningResourceService
from app.services.local_ai_service import LocalAIService
from app.services.onboarding_service import OnboardingService
from app.services.study_service import StudyService

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


def get_learning_resource_service(db: DbSession) -> LearningResourceService:
    """Compose a :class:`LearningResourceService` backed by SQLAlchemy."""
    return LearningResourceService(
        repository=SqlAlchemyLearningResourceRepository(db),
        onboarding_repository=SqlAlchemyOnboardingRepository(db),
    )


def get_study_service(db: DbSession) -> StudyService:
    """Compose a :class:`StudyService` backed by SQLAlchemy."""
    return StudyService(
        study_repository=SqlAlchemyStudyRepository(db),
        learning_repository=SqlAlchemyLearningResourceRepository(db),
        onboarding_repository=SqlAlchemyOnboardingRepository(db),
    )


def get_health_service(db: DbSession, settings: AppSettings) -> HealthService:
    """Compose a :class:`HealthService`."""
    return HealthService(db, settings)


OnboardingServiceDep = Annotated[OnboardingService, Depends(get_onboarding_service)]
DeviceServiceDep = Annotated[DeviceService, Depends(get_device_service)]
LocalAIServiceDep = Annotated[LocalAIService, Depends(get_local_ai_service)]
LearningResourceServiceDep = Annotated[
    LearningResourceService, Depends(get_learning_resource_service)
]
StudyServiceDep = Annotated[StudyService, Depends(get_study_service)]
HealthServiceDep = Annotated[HealthService, Depends(get_health_service)]
