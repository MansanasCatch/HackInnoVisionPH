"""Use cases for version-aware study sessions and progress updates."""

from app.core.exceptions import NotFoundError
from app.db.base import utc_now
from app.models.study import StudyAnswer, StudySession, UserVersionProgress
from app.repositories.learning_resource_repository import AbstractLearningResourceRepository
from app.repositories.onboarding_repository import AbstractOnboardingRepository
from app.repositories.study_repository import AbstractStudyRepository
from app.schemas.learning_resource import VersionProgressRead
from app.schemas.study import (
    StudyAnswerCreate,
    StudyAnswerRead,
    StudySessionComplete,
    StudySessionCompleteResponse,
    StudySessionRead,
    StudySessionStart,
)


class StudyService:
    """Orchestrates study attempts, answer records, and progress summaries."""

    def __init__(
        self,
        study_repository: AbstractStudyRepository,
        learning_repository: AbstractLearningResourceRepository,
        onboarding_repository: AbstractOnboardingRepository,
    ) -> None:
        self._study_repo = study_repository
        self._learning_repo = learning_repository
        self._onboarding_repo = onboarding_repository

    def start_session(self, payload: StudySessionStart) -> StudySessionRead:
        """Start a study session for one exact learning resource version."""
        self._ensure_onboarding_exists(payload.onboarding_id)
        self._ensure_version_belongs_to_onboarding(
            onboarding_id=payload.onboarding_id,
            resource_version_id=payload.resource_version_id,
        )
        first_time = not self._study_repo.has_session_for_version(
            onboarding_id=payload.onboarding_id,
            resource_version_id=payload.resource_version_id,
        )
        session = StudySession(
            onboarding_id=payload.onboarding_id,
            resource_version_id=payload.resource_version_id,
            mode=payload.mode.value,
            source=payload.source.value,
            first_time_for_version=first_time,
        )
        saved = self._study_repo.add_session(session)
        return StudySessionRead.model_validate(saved)

    def get_session(self, session_id: int) -> StudySessionRead:
        """Fetch a study session by ID."""
        return StudySessionRead.model_validate(self._get_session_or_raise(session_id))

    def add_answer(self, session_id: int, payload: StudyAnswerCreate) -> StudyAnswerRead:
        """Record one answer in a study session."""
        self._get_session_or_raise(session_id)
        answer = StudyAnswer(
            study_session_id=session_id,
            question_id=payload.question_id,
            concept_id=payload.concept_id,
            concept_name=payload.concept_name,
            student_answer=payload.student_answer,
            correct_answer=payload.correct_answer,
            is_correct=payload.is_correct,
            time_taken_seconds=payload.time_taken_seconds,
            confidence=payload.confidence,
            hints_used=payload.hints_used,
        )
        saved = self._study_repo.add_answer(answer)
        return StudyAnswerRead.model_validate(saved)

    def complete_session(
        self, session_id: int, payload: StudySessionComplete
    ) -> StudySessionCompleteResponse:
        """Complete a session, score it, and update version progress."""
        session = self._get_session_or_raise(session_id)
        answers = self._study_repo.list_answers(session_id)

        total_items = payload.total_items
        if total_items is None:
            total_items = len(answers)

        correct_items = payload.correct_items
        if correct_items is None:
            correct_items = sum(1 for answer in answers if answer.is_correct)

        accuracy = (correct_items / total_items * 100) if total_items else 0.0
        completed_at = utc_now()

        session.score = payload.score
        session.total_items = total_items
        session.correct_items = correct_items
        session.accuracy = round(accuracy, 2)
        session.time_spent_seconds = payload.time_spent_seconds
        session.completed_at = completed_at
        saved_session = self._study_repo.update_session(session)

        progress = self._upsert_progress(saved_session)

        return StudySessionCompleteResponse(
            session=StudySessionRead.model_validate(saved_session),
            progress=progress,
        )

    def _upsert_progress(self, session: StudySession) -> VersionProgressRead:
        progress = self._study_repo.get_progress(
            onboarding_id=session.onboarding_id,
            resource_version_id=session.resource_version_id,
        )

        completed_at = session.completed_at or utc_now()
        if progress is None:
            progress = UserVersionProgress(
                onboarding_id=session.onboarding_id,
                resource_version_id=session.resource_version_id,
                first_started_at=session.started_at,
                last_studied_at=completed_at,
                attempts_count=1,
                best_score=session.score,
                latest_score=session.score,
                latest_accuracy=session.accuracy,
                mastery_state=self._mastery_state_for_accuracy(session.accuracy),
            )
            saved = self._study_repo.add_progress(progress)
        else:
            progress.attempts_count += 1
            progress.last_studied_at = completed_at
            progress.latest_score = session.score
            progress.latest_accuracy = session.accuracy
            if session.score is not None:
                if progress.best_score is None:
                    progress.best_score = session.score
                else:
                    progress.best_score = max(progress.best_score, session.score)
            progress.mastery_state = self._mastery_state_for_accuracy(session.accuracy)
            saved = self._study_repo.update_progress(progress)

        return VersionProgressRead(
            onboarding_id=saved.onboarding_id,
            resource_version_id=saved.resource_version_id,
            first_time_for_version=False,
            attempts_count=saved.attempts_count,
            latest_score=saved.latest_score,
            best_score=saved.best_score,
            latest_accuracy=saved.latest_accuracy,
            mastery_state=saved.mastery_state,
            first_started_at=saved.first_started_at,
            last_studied_at=saved.last_studied_at,
        )

    def _ensure_onboarding_exists(self, onboarding_id: int) -> None:
        if self._onboarding_repo.get(onboarding_id) is None:
            raise NotFoundError(f"Onboarding account with ID {onboarding_id} not found.")

    def _ensure_version_belongs_to_onboarding(
        self, *, onboarding_id: int, resource_version_id: int
    ) -> None:
        version = self._learning_repo.get_version(resource_version_id)
        if version is None:
            raise NotFoundError(
                f"Learning resource version with ID {resource_version_id} was not found."
            )
        if version.learning_resource.onboarding_id != onboarding_id:
            raise NotFoundError(
                f"Learning resource version with ID {resource_version_id} was not found."
            )

    def _get_session_or_raise(self, session_id: int) -> StudySession:
        session = self._study_repo.get_session(session_id)
        if session is None:
            raise NotFoundError(f"Study session with ID {session_id} was not found.")
        return session

    @staticmethod
    def _mastery_state_for_accuracy(accuracy: float) -> str:
        if accuracy >= 80:
            return "mastered"
        if accuracy >= 50:
            return "learning"
        return "needs_practice"
