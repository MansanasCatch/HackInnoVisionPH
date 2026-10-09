"""Endpoint for the per-concept knowledge map."""

from typing import Annotated

from fastapi import APIRouter, Query

from app.api.deps import StudyServiceDep
from app.schemas.knowledge_map import KnowledgeMapResponse

router = APIRouter(prefix="/knowledge-map", tags=["Knowledge Map"])


@router.get("", response_model=KnowledgeMapResponse, summary="Get a learner's knowledge map")
def get_knowledge_map(
    service: StudyServiceDep,
    onboarding_id: Annotated[int, Query(ge=1)],
) -> KnowledgeMapResponse:
    """Mastery per concept, based on each concept's latest three completed sessions."""
    return service.get_knowledge_map(onboarding_id=onboarding_id)
