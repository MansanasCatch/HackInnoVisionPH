"""ORM models. Import every model here so Alembic autogenerate can discover it."""

from app.models.device import DeviceSpecs
from app.models.onboarding import OnboardingProfile

__all__ = ["DeviceSpecs", "OnboardingProfile"]
