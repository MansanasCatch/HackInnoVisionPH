"""Data-access repository for study sessions, answers, and progress."""

from collections.abc import Sequence
from typing import Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.study import StudyAnswer, StudySession, UserVersionProgress


class AbstractStudyRepository(Protocol):
    """Interface defining study-session persistence operations."""

    def add_session(self, session: StudySession) -> StudySession:
        """Persist a new study session."""
        ...

    def get_session(self, session_id: int) -> StudySession | None:
        """Fetch a study session by ID."""
        ...

    def has_session_for_version(self, *, onboarding_id: int, resource_version_id: int) -> bool:
        """Return whether the learner has already started this version."""
        ...

    def add_answer(self, answer: StudyAnswer) -> StudyAnswer:
        """Persist one answer record."""
        ...

    def list_answers(self, session_id: int) -> Sequence[StudyAnswer]:
        """List answer records for a study session."""
        ...

    def update_session(self, session: StudySession) -> StudySession:
        """Persist changes to a study session."""
        ...

    def get_progress(
        self, *, onboarding_id: int, resource_version_id: int
    ) -> UserVersionProgress | None:
        """Fetch progress for a learner and version."""
        ...

    def add_progress(self, progress: UserVersionProgress) -> UserVersionProgress:
        """Persist a new progress record."""
        ...

    def update_progress(self, progress: UserVersionProgress) -> UserVersionProgress:
        """Persist changes to a progress record."""
        ...


class SqlAlchemyStudyRepository(AbstractStudyRepository):
    """Production study repository backed by SQLAlchemy."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def add_session(self, session: StudySession) -> StudySession:
        self._session.add(session)
        self._session.commit()
        self._session.refresh(session)
        return session

    def get_session(self, session_id: int) -> StudySession | None:
        return self._session.get(StudySession, session_id)

    def has_session_for_version(self, *, onboarding_id: int, resource_version_id: int) -> bool:
        statement = (
            select(StudySession.id)
            .where(
                StudySession.onboarding_id == onboarding_id,
                StudySession.resource_version_id == resource_version_id,
            )
            .limit(1)
        )
        return self._session.scalars(statement).first() is not None

    def add_answer(self, answer: StudyAnswer) -> StudyAnswer:
        self._session.add(answer)
        self._session.commit()
        self._session.refresh(answer)
        return answer

    def list_answers(self, session_id: int) -> Sequence[StudyAnswer]:
        statement = (
            select(StudyAnswer)
            .where(StudyAnswer.study_session_id == session_id)
            .order_by(StudyAnswer.created_at.asc(), StudyAnswer.id.asc())
        )
        return self._session.scalars(statement).all()

    def update_session(self, session: StudySession) -> StudySession:
        self._session.add(session)
        self._session.commit()
        self._session.refresh(session)
        return session

    def get_progress(
        self, *, onboarding_id: int, resource_version_id: int
    ) -> UserVersionProgress | None:
        statement = select(UserVersionProgress).where(
            UserVersionProgress.onboarding_id == onboarding_id,
            UserVersionProgress.resource_version_id == resource_version_id,
        )
        return self._session.scalars(statement).first()

    def add_progress(self, progress: UserVersionProgress) -> UserVersionProgress:
        self._session.add(progress)
        self._session.commit()
        self._session.refresh(progress)
        return progress

    def update_progress(self, progress: UserVersionProgress) -> UserVersionProgress:
        self._session.add(progress)
        self._session.commit()
        self._session.refresh(progress)
        return progress
