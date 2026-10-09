"""Data-access repository for onboarding profiles."""

from collections.abc import Sequence
from typing import Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.onboarding import OnboardingProfile


class AbstractOnboardingRepository(Protocol):
    """Interface defining operations for onboarding profile storage."""

    def add(self, profile: OnboardingProfile) -> OnboardingProfile:
        """Add a new onboarding profile."""
        ...

    def get(self, profile_id: int) -> OnboardingProfile | None:
        """Fetch an onboarding profile by its primary key."""
        ...

    def get_by_username(self, username: str) -> OnboardingProfile | None:
        """Fetch an onboarding profile by username."""
        ...

    def list(self, *, limit: int = 50, offset: int = 0) -> Sequence[OnboardingProfile]:
        """Fetch all onboarding profiles with pagination."""
        ...

    def update(self, profile: OnboardingProfile) -> OnboardingProfile:
        """Persist changes made to an onboarding profile."""
        ...


class SqlAlchemyOnboardingRepository(AbstractOnboardingRepository):
    """Production repository implementation backed by SQLAlchemy."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, profile: OnboardingProfile) -> OnboardingProfile:
        self._session.add(profile)
        self._session.commit()
        self._session.refresh(profile)
        return profile

    def get(self, profile_id: int) -> OnboardingProfile | None:
        return self._session.get(OnboardingProfile, profile_id)

    def get_by_username(self, username: str) -> OnboardingProfile | None:
        statement = select(OnboardingProfile).where(
            OnboardingProfile.username.ilike(username.strip())
        )
        return self._session.scalars(statement).first()

    def list(self, *, limit: int = 50, offset: int = 0) -> Sequence[OnboardingProfile]:
        statement = (
            select(OnboardingProfile)
            .order_by(OnboardingProfile.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return self._session.scalars(statement).all()

    def update(self, profile: OnboardingProfile) -> OnboardingProfile:
        self._session.add(profile)
        self._session.commit()
        self._session.refresh(profile)
        return profile
