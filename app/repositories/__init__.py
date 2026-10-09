"""Data-access layer. Repositories hide persistence details from the services."""

from app.repositories.device_repository import (
    AbstractDeviceRepository,
    SqlAlchemyDeviceRepository,
)
from app.repositories.learning_resource_repository import (
    AbstractLearningResourceRepository,
    SqlAlchemyLearningResourceRepository,
)
from app.repositories.onboarding_repository import (
    AbstractOnboardingRepository,
    SqlAlchemyOnboardingRepository,
)
from app.repositories.study_repository import (
    AbstractStudyRepository,
    SqlAlchemyStudyRepository,
)

__all__ = [
    "AbstractDeviceRepository",
    "AbstractLearningResourceRepository",
    "AbstractOnboardingRepository",
    "AbstractStudyRepository",
    "SqlAlchemyDeviceRepository",
    "SqlAlchemyLearningResourceRepository",
    "SqlAlchemyOnboardingRepository",
    "SqlAlchemyStudyRepository",
]
