"""ORM records for version-aware study sessions and progress."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, utc_now
from app.models.learning_resource import LearningResourceVersion


class StudySession(Base, TimestampMixin):
    """A learner's attempt against one exact learning resource version."""

    __tablename__ = "study_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    onboarding_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("onboardings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    resource_version_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("learning_resource_versions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    mode: Mapped[str] = mapped_column(String(50), nullable=False)
    source: Mapped[str] = mapped_column(String(50), nullable=False)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_items: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    correct_items: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    accuracy: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    time_spent_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    first_time_for_version: Mapped[bool] = mapped_column(Boolean, nullable=False)

    resource_version: Mapped[LearningResourceVersion] = relationship(
        "LearningResourceVersion",
        back_populates="study_sessions",
    )
    answers: Mapped[list["StudyAnswer"]] = relationship(
        "StudyAnswer",
        back_populates="study_session",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<StudySession id={self.id} version_id={self.resource_version_id}>"


class StudyAnswer(Base, TimestampMixin):
    """One recorded answer inside a study session."""

    __tablename__ = "study_answers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    study_session_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("study_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question_id: Mapped[str] = mapped_column(String(120), nullable=False)
    concept_id: Mapped[str] = mapped_column(String(120), nullable=False)
    concept_name: Mapped[str] = mapped_column(String(160), default="", nullable=False)
    student_answer: Mapped[str] = mapped_column(Text, default="", nullable=False)
    correct_answer: Mapped[str] = mapped_column(Text, default="", nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    time_taken_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    confidence: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    hints_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    study_session: Mapped[StudySession] = relationship(
        "StudySession",
        back_populates="answers",
    )

    def __repr__(self) -> str:
        return f"<StudyAnswer id={self.id} session_id={self.study_session_id}>"


class UserVersionProgress(Base, TimestampMixin):
    """Progress summary for one learner and one learning resource version."""

    __tablename__ = "user_version_progress"
    __table_args__ = (
        UniqueConstraint(
            "onboarding_id",
            "resource_version_id",
            name="uq_user_version_progress_onboarding_version",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    onboarding_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("onboardings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    resource_version_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("learning_resource_versions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    first_started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_studied_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    attempts_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    best_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    latest_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    latest_accuracy: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    mastery_state: Mapped[str] = mapped_column(String(50), default="new", nullable=False)

    resource_version: Mapped[LearningResourceVersion] = relationship(
        "LearningResourceVersion",
        back_populates="progress_records",
    )

    def __repr__(self) -> str:
        return (
            "<UserVersionProgress "
            f"onboarding_id={self.onboarding_id} version_id={self.resource_version_id}>"
        )
