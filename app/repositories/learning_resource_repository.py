"""Data-access repositories for learning resource records and versions."""

from collections.abc import Sequence
from typing import Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.learning_resource import LearningResource, LearningResourceVersion
from app.models.study import (
    ArchivedVersionAnalytics,
    StudyAnswer,
    StudySession,
    UserVersionProgress,
)


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

    def create_version(
        self, version: LearningResourceVersion, *, commit: bool = True
    ) -> tuple[LearningResourceVersion, list[int]]:
        """Persist a version and archive full versions beyond the latest three."""
        ...

    def list_archived_analytics(self, resource_id: int) -> Sequence[ArchivedVersionAnalytics]:
        """Return compact analytics for removed versions."""
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

    def create_version(
        self, version: LearningResourceVersion, *, commit: bool = True
    ) -> tuple[LearningResourceVersion, list[int]]:
        statement = select(LearningResourceVersion).where(
            LearningResourceVersion.learning_resource_id == version.learning_resource_id
        )
        for existing in self._session.scalars(statement):
            existing.is_current = False

        self._session.add(version)
        self._session.flush()
        archived = self._archive_excess_versions(version.learning_resource_id)
        if commit:
            self._session.commit()
            self._session.refresh(version)
        return version, archived

    def list_archived_analytics(self, resource_id: int) -> Sequence[ArchivedVersionAnalytics]:
        statement = (
            select(ArchivedVersionAnalytics)
            .where(ArchivedVersionAnalytics.learning_resource_id == resource_id)
            .order_by(ArchivedVersionAnalytics.version_number.desc())
        )
        return self._session.scalars(statement).all()

    def _archive_excess_versions(self, resource_id: int) -> list[int]:
        versions = list(
            self._session.scalars(
                select(LearningResourceVersion)
                .where(LearningResourceVersion.learning_resource_id == resource_id)
                .order_by(LearningResourceVersion.version_number.desc())
            ).all()
        )
        archived_numbers: list[int] = []
        for old_version in versions[3:]:
            sessions = list(
                self._session.scalars(
                    select(StudySession)
                    .where(StudySession.resource_version_id == old_version.id)
                    .order_by(StudySession.completed_at.asc(), StudySession.id.asc())
                ).all()
            )
            completed = [session for session in sessions if session.completed_at is not None]
            session_ids = [session.id for session in completed]
            answers = (
                self._session.scalars(
                    select(StudyAnswer).where(StudyAnswer.study_session_id.in_(session_ids))
                ).all()
                if session_ids
                else []
            )
            concepts: dict[str, dict] = {}
            for answer in answers:
                entry = concepts.setdefault(
                    answer.concept_id,
                    {"concept_id": answer.concept_id, "concept_name": answer.concept_name,
                     "answered": 0, "correct": 0, "time_seconds": 0, "hints_used": 0},
                )
                entry["answered"] += 1
                entry["correct"] += int(answer.is_correct)
                entry["time_seconds"] += answer.time_taken_seconds
                entry["hints_used"] += answer.hints_used

            self._session.add(
                ArchivedVersionAnalytics(
                    learning_resource_id=resource_id,
                    onboarding_id=old_version.learning_resource.onboarding_id,
                    version_number=old_version.version_number,
                    attempts_count=len(completed),
                    total_items=sum(session.total_items for session in completed),
                    correct_items=sum(session.correct_items for session in completed),
                    total_time_seconds=sum(session.time_spent_seconds for session in completed),
                    best_score=max(
                        (session.score for session in completed if session.score is not None),
                        default=None,
                    ),
                    latest_score=completed[-1].score if completed else None,
                    concept_stats=list(concepts.values()),
                )
            )
            self._session.delete(old_version)
            archived_numbers.append(old_version.version_number)
        self._session.flush()
        return archived_numbers

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
