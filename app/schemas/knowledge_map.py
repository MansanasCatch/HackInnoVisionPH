"""Pydantic schemas for the per-concept knowledge map."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

KnowledgeState = Literal["strong", "developing", "needs_practice"]


class KnowledgeMapItem(BaseModel):
    """Mastery evidence for one concept, from the learner's latest three sessions."""

    concept_id: str
    concept_name: str
    accuracy: float = Field(description="Percent correct across the evidence window")
    answers: int = Field(description="Answers counted in the evidence window")
    sessions: int = Field(description="Distinct sessions counted (max 3)")
    state: KnowledgeState
    last_seen: datetime | None = None


class KnowledgeMapResponse(BaseModel):
    """Knowledge map for a learner. Concepts needing practice are listed first."""

    onboarding_id: int
    items: list[KnowledgeMapItem] = Field(default_factory=list)
