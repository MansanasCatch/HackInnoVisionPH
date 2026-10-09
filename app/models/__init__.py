"""ORM models. Import every model here so Alembic autogenerate can discover it."""

from app.models.onboarding import OnboardingProfile

__all__ = ["OnboardingProfile"]
