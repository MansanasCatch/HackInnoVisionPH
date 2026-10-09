"""Pydantic schemas for version-aware study sessions."""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.learning_resource import VersionProgressRead


class StudyMode(StrEnum):
    """Current study modes, kept lightweight for future expansion."""

    LEARN = "learn"
    PRACTICE = "practice"
    REVIEW = "review"
    QUIZ = "quiz"
    EXAM = "exam"


class StudySource(StrEnum):
    """Current study resource sources."""

    STUDY = "study"
    SUMMARY = "summary"
    REVIEWER = "reviewer"
    FLASHCARDS = "flashcards"
    PRACTICE_QUIZ = "practice_quiz"
    MOCK_EXAM = "mock_exam"
    QA_REVIEWER = "qa_reviewer"


class StudySessionStart(BaseModel):
    """Payload used to start a study session for one resource version."""

    onboarding_id: int = Field(ge=1)
    resource_version_id: int = Field(ge=1)
    mode: StudyMode = StudyMode.PRACTICE
    source: StudySource = StudySource.PRACTICE_QUIZ


class StudySessionRead(BaseModel):
    """Study session record returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    onboarding_id: int
    resource_version_id: int
    mode: str
    source: str
    started_at: datetime
    completed_at: datetime | None
    score: int | None
    total_items: int
    correct_items: int
    accuracy: float
    time_spent_seconds: int
    first_time_for_version: bool
    created_at: datetime
    updated_at: datetime


class StudyAnswerCreate(BaseModel):
    """Payload used to record one answer in a study session."""

    model_config = ConfigDict(str_strip_whitespace=True)

    question_id: str = Field(min_length=1, max_length=120)
    concept_id: str = Field(min_length=1, max_length=120)
    concept_name: str = Field(default="", max_length=160)
    student_answer: str = ""
    correct_answer: str = ""
    is_correct: bool = False
    time_taken_seconds: int = Field(default=0, ge=0)
    confidence: int = Field(default=0, ge=0, le=5)
    hints_used: int = Field(default=0, ge=0)


class StudyAnswerRead(BaseModel):
    """Answer record returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    study_session_id: int
    question_id: str
    concept_id: str
    concept_name: str
    student_answer: str
    correct_answer: str
    is_correct: bool
    time_taken_seconds: int
    confidence: int
    hints_used: int
    created_at: datetime
    updated_at: datetime


class StudySessionComplete(BaseModel):
    """Payload used to complete and score a study session."""

    score: int = Field(ge=0)
    total_items: int | None = Field(default=None, ge=0)
    correct_items: int | None = Field(default=None, ge=0)
    time_spent_seconds: int = Field(default=0, ge=0)


class StudySessionCompleteResponse(BaseModel):
    """Response returned after completing a session and updating progress."""

    session: StudySessionRead
    progress: VersionProgressRead
    new_version_id: int | None = None
    archived_version_number: int | None = None
