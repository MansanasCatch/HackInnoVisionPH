"""Use cases for version-aware study sessions and progress updates."""

from collections.abc import Sequence
from copy import deepcopy

from sqlalchemy.exc import IntegrityError

from app.core.exceptions import ConflictError, NotFoundError
from app.db.base import utc_now
from app.models.learning_resource import LearningResourceVersion
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
        session = self._get_session_or_raise(session_id)
        if session.completed_at is not None:
            raise ConflictError("Cannot add answers to a completed study session.")
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
        """Complete a session and advance only the current resource version."""
        session = self._get_session_or_raise(session_id)
        version = self._learning_repo.get_version(session.resource_version_id)
        if version is None:
            raise NotFoundError("The session's learning resource version was removed.")

        try:
            self._study_repo.lock_resource(version.learning_resource_id)
            self._study_repo.refresh(session)
            version = self._learning_repo.get_version(session.resource_version_id)
            if version is None:
                raise NotFoundError("The session's learning resource version was removed.")
            self._study_repo.refresh(version)
            if session.completed_at is not None:
                progress = self._study_repo.get_progress(
                    onboarding_id=session.onboarding_id,
                    resource_version_id=session.resource_version_id,
                )
                if progress is None:
                    raise ConflictError("Completed session has no progress record.")
                result = StudySessionCompleteResponse(
                    session=StudySessionRead.model_validate(session),
                    progress=self._progress_read(progress),
                    new_version_id=session.generated_version_id,
                    archived_version_number=session.archived_version_number,
                )
                self._study_repo.commit()
                return result

            answers = self._study_repo.list_answers(session_id)
            total_items = payload.total_items if payload.total_items is not None else len(answers)
            correct_items = (
                payload.correct_items
                if payload.correct_items is not None
                else sum(1 for answer in answers if answer.is_correct)
            )
            if correct_items > total_items:
                raise ConflictError("Correct items cannot exceed total items.")

            session.score = payload.score
            session.total_items = total_items
            session.correct_items = correct_items
            session.accuracy = round(correct_items / total_items * 100, 2) if total_items else 0.0
            session.time_spent_seconds = payload.time_spent_seconds
            session.completed_at = utc_now()
            self._study_repo.update_session(session)
            progress = self._upsert_progress(session)

            if version.is_current:
                number = self._learning_repo.next_version_number(version.learning_resource_id)
                successor = LearningResourceVersion(
                    learning_resource_id=version.learning_resource_id,
                    version_number=number,
                    title=f"{version.learning_resource.title} v{number}",
                    summary=version.summary,
                    content=self._next_version_content(version, session, answers),
                    resource_types=list(version.resource_types),
                    topics=list(version.topics),
                    is_current=True,
                )
                saved, archived = self._learning_repo.create_version(successor, commit=False)
                session.generated_version_id = saved.id
                session.archived_version_number = archived[0] if archived else None
                self._study_repo.update_session(session)

            result = StudySessionCompleteResponse(
                session=StudySessionRead.model_validate(session),
                progress=progress,
                new_version_id=session.generated_version_id,
                archived_version_number=session.archived_version_number,
            )
            self._study_repo.commit()
            return result
        except IntegrityError as exc:
            self._study_repo.rollback()
            raise ConflictError(
                "Resource version changed during completion; retry the request."
            ) from exc
        except Exception:
            self._study_repo.rollback()
            raise

    @staticmethod
    def _next_version_content(
        version: LearningResourceVersion, session: StudySession, answers: Sequence[StudyAnswer]
    ) -> dict:
        content = deepcopy(version.content)
        missed: dict[str, dict] = {}
        for answer in answers:
            if not answer.is_correct:
                missed.setdefault(
                    answer.concept_id,
                    {
                        "concept_id": answer.concept_id,
                        "concept_name": answer.concept_name,
                        "review_answer": answer.correct_answer,
                    },
                )
        content["adaptive_review"] = {
            "based_on_version": version.version_number,
            "based_on_session_id": session.id,
            "score": session.score,
            "accuracy": session.accuracy,
            "priority_concepts": list(missed.values()),
        }
        return content

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

        return self._progress_read(saved)

    @staticmethod
    def _progress_read(saved: UserVersionProgress) -> VersionProgressRead:
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
