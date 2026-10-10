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

    def delete(self, profile: OnboardingProfile) -> None:
        """Delete an onboarding profile from storage."""
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

    def delete(self, profile: OnboardingProfile) -> None:
        profile_id = profile.id
        from app.models.device import DeviceSpecs
        from app.models.learning_resource import LearningResource, LearningResourceVersion
        from app.models.study import (
            ArchivedVersionAnalytics,
            StudyAnswer,
            StudySession,
            UserVersionProgress,
        )

        # 1. Device specs
        self._session.query(DeviceSpecs).filter(DeviceSpecs.onboarding_id == profile_id).delete(synchronize_session=False)

        # 2. Study answers & sessions
        session_ids = [s[0] for s in self._session.query(StudySession.id).filter(StudySession.onboarding_id == profile_id).all()]
        if session_ids:
            self._session.query(StudyAnswer).filter(StudyAnswer.study_session_id.in_(session_ids)).delete(synchronize_session=False)
            self._session.query(StudySession).filter(StudySession.id.in_(session_ids)).delete(synchronize_session=False)

        # 3. Learning resource versions & resources
        resource_ids = [r[0] for r in self._session.query(LearningResource.id).filter(LearningResource.onboarding_id == profile_id).all()]
        if resource_ids:
            version_ids = [v[0] for v in self._session.query(LearningResourceVersion.id).filter(LearningResourceVersion.learning_resource_id.in_(resource_ids)).all()]
            if version_ids:
                self._session.query(UserVersionProgress).filter(UserVersionProgress.resource_version_id.in_(version_ids)).delete(synchronize_session=False)
                self._session.query(StudySession).filter(StudySession.resource_version_id.in_(version_ids)).delete(synchronize_session=False)
                self._session.query(LearningResourceVersion).filter(LearningResourceVersion.id.in_(version_ids)).delete(synchronize_session=False)
            self._session.query(LearningResource).filter(LearningResource.id.in_(resource_ids)).delete(synchronize_session=False)

        # 4. Any remaining user version progress by onboarding_id
        self._session.query(UserVersionProgress).filter(UserVersionProgress.onboarding_id == profile_id).delete(synchronize_session=False)

        # 5. Archived version analytics
        self._session.query(ArchivedVersionAnalytics).filter(ArchivedVersionAnalytics.onboarding_id == profile_id).delete(synchronize_session=False)

        # 6. Delete onboarding profile itself
        self._session.delete(profile)
        self._session.commit()

