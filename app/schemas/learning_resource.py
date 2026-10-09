"""Pydantic schemas for learning resource records and versions."""

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class StudyResourceType(StrEnum):
    """Current supported generated study resource types."""

    SUMMARY = "summary"
    REVIEWER = "reviewer"
    FLASHCARDS = "flashcards"
    PRACTICE_QUIZ = "practice_quiz"
    MOCK_EXAM = "mock_exam"
    QA_REVIEWER = "qa_reviewer"


class LearningResourceCreate(BaseModel):
    """Payload used to create a learning resource record."""

    model_config = ConfigDict(str_strip_whitespace=True)

    onboarding_id: int = Field(ge=1, description="Onboarding account ID")
    title: str = Field(min_length=1, max_length=160)
    subject: str = Field(default="", max_length=100)
    source_label: str = Field(default="", max_length=255)


class LearningResourceRead(BaseModel):
    """Learning resource record returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    onboarding_id: int
    title: str
    subject: str
    source_label: str
    created_at: datetime
    updated_at: datetime


class LearningResourceVersionCreate(BaseModel):
    """Payload used to create a new version for a learning resource."""

    model_config = ConfigDict(str_strip_whitespace=True)

    title: str | None = Field(default=None, max_length=160)
    summary: str = ""
    content: dict[str, Any] = Field(default_factory=dict)
    resource_types: list[StudyResourceType] = Field(default_factory=list)
    topics: list[str] = Field(default_factory=list)


class LearningResourceVersionRead(BaseModel):
    """Version record returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    learning_resource_id: int
    version_number: int
    title: str
    summary: str
    content: dict[str, Any]
    resource_types: list[str]
    topics: list[str]
    is_current: bool
    created_at: datetime
    updated_at: datetime


class VersionProgressRead(BaseModel):
    """Progress summary for a learner on a specific version."""

    onboarding_id: int
    resource_version_id: int
    first_time_for_version: bool
    attempts_count: int
    latest_score: int | None = None
    best_score: int | None = None
    latest_accuracy: float = 0.0
    mastery_state: str = "new"
    first_started_at: datetime | None = None
    last_studied_at: datetime | None = None


class GenerationInfo(BaseModel):
    """Metadata about how study materials were generated."""

    model_used: str = ""
    is_ollama_online: bool = False
    execution_time_seconds: float = 0.0
    warnings: list[str] = Field(default_factory=list)


class GeneratedLearningResource(BaseModel):
    """Result of generating and persisting a learning resource from user material."""

    resource: LearningResourceRead
    version: LearningResourceVersionRead
    generation: GenerationInfo


class ArchivedVersionAnalyticsRead(BaseModel):
    """Compact metrics for a version no longer available to study."""

    model_config = ConfigDict(from_attributes=True)

    learning_resource_id: int
    version_number: int
    attempts_count: int
    total_items: int
    correct_items: int
    total_time_seconds: int
    best_score: int | None
    latest_score: int | None
    concept_stats: list[dict[str, Any]]

