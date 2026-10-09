"""Data-access repositories for learning resource records and versions."""

from collections.abc import Sequence
from typing import Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.learning_resource import LearningResource, LearningResourceVersion
from app.models.study import UserVersionProgress


class AbstractLearningResourceRepository(Protocol):
    """Interface defining learning resource persistence operations."""

    def add_resource(self, resource: LearningResource) -> LearningResource:
        """Persist a new learning resource record."""
        ...

    def get_resource(self, resource_id: int) -> LearningResource | None:
        """Fetch a learning resource record by ID."""
        ...

    def list_resources(
        self, *, onboarding_id: int, limit: int = 50, offset: int = 0
    ) -> Sequence[LearningResource]:
        """List learning resource records for one onboarding account."""
        ...

    def create_version(self, version: LearningResourceVersion) -> LearningResourceVersion:
        """Persist a new current version and mark older versions not current."""
        ...

    def get_version(self, version_id: int) -> LearningResourceVersion | None:
        """Fetch a resource version by ID."""
        ...

    def list_versions(
        self, *, resource_id: int, limit: int = 3
    ) -> Sequence[LearningResourceVersion]:
        """List latest versions for one resource."""
        ...

    def next_version_number(self, resource_id: int) -> int:
        """Return the next version number for a resource."""
        ...

    def get_progress(
        self, *, onboarding_id: int, resource_version_id: int
    ) -> UserVersionProgress | None:
        """Fetch progress for a learner and version."""
        ...


class SqlAlchemyLearningResourceRepository(AbstractLearningResourceRepository):
    """Production learning resource repository backed by SQLAlchemy."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def add_resource(self, resource: LearningResource) -> LearningResource:
        self._session.add(resource)
        self._session.commit()
        self._session.refresh(resource)
        return resource

    def get_resource(self, resource_id: int) -> LearningResource | None:
        return self._session.get(LearningResource, resource_id)

    def list_resources(
        self, *, onboarding_id: int, limit: int = 50, offset: int = 0
    ) -> Sequence[LearningResource]:
        statement = (
            select(LearningResource)
            .where(LearningResource.onboarding_id == onboarding_id)
            .order_by(LearningResource.updated_at.desc(), LearningResource.id.desc())
            .offset(offset)
            .limit(limit)
        )
        return self._session.scalars(statement).all()

    def create_version(self, version: LearningResourceVersion) -> LearningResourceVersion:
        statement = select(LearningResourceVersion).where(
            LearningResourceVersion.learning_resource_id == version.learning_resource_id
        )
        for existing in self._session.scalars(statement):
            existing.is_current = False

        self._session.add(version)
        self._session.commit()
        self._session.refresh(version)
        return version

    def get_version(self, version_id: int) -> LearningResourceVersion | None:
        return self._session.get(LearningResourceVersion, version_id)

    def list_versions(
        self, *, resource_id: int, limit: int = 3
    ) -> Sequence[LearningResourceVersion]:
        statement = (
            select(LearningResourceVersion)
            .where(LearningResourceVersion.learning_resource_id == resource_id)
            .order_by(
                LearningResourceVersion.version_number.desc(),
                LearningResourceVersion.id.desc(),
            )
            .limit(limit)
        )
        return self._session.scalars(statement).all()

    def next_version_number(self, resource_id: int) -> int:
        statement = (
            select(LearningResourceVersion.version_number)
            .where(LearningResourceVersion.learning_resource_id == resource_id)
            .order_by(LearningResourceVersion.version_number.desc())
            .limit(1)
        )
        latest = self._session.scalars(statement).first()
        return 1 if latest is None else latest + 1

    def get_progress(
        self, *, onboarding_id: int, resource_version_id: int
    ) -> UserVersionProgress | None:
        statement = select(UserVersionProgress).where(
            UserVersionProgress.onboarding_id == onboarding_id,
            UserVersionProgress.resource_version_id == resource_version_id,
        )
        return self._session.scalars(statement).first()
