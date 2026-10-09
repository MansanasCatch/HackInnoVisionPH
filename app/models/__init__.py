"""ORM models. Import every model here so Alembic autogenerate can discover it."""

from app.models.device import DeviceSpecs
from app.models.learning_resource import LearningResource, LearningResourceVersion
from app.models.onboarding import OnboardingProfile
from app.models.study import StudyAnswer, StudySession, UserVersionProgress

__all__ = [
    "DeviceSpecs",
    "LearningResource",
    "LearningResourceVersion",
    "OnboardingProfile",
    "StudyAnswer",
    "StudySession",
    "UserVersionProgress",
]
