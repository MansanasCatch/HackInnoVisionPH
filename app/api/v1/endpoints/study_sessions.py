"""Endpoints for version-aware study sessions."""

from fastapi import APIRouter, status

from app.api.deps import StudyServiceDep
from app.schemas.study import (
    StudyAnswerCreate,
    StudyAnswerRead,
    StudySessionComplete,
    StudySessionCompleteResponse,
    StudySessionRead,
    StudySessionStart,
)

router = APIRouter(prefix="/study-sessions", tags=["Study Sessions"])


@router.post(
    "",
    response_model=StudySessionRead,
    status_code=status.HTTP_201_CREATED,
    summary="Start a study session",
)
def start_study_session(
    payload: StudySessionStart,
    service: StudyServiceDep,
) -> StudySessionRead:
    """Start a study session for one exact learning resource version."""
    return service.start_session(payload)


@router.get(
    "/{session_id}",
    response_model=StudySessionRead,
    summary="Get a study session",
)
def get_study_session(
    session_id: int,
    service: StudyServiceDep,
) -> StudySessionRead:
    """Fetch a study session by ID."""
    return service.get_session(session_id)


@router.post(
    "/{session_id}/answers",
    response_model=StudyAnswerRead,
    status_code=status.HTTP_201_CREATED,
    summary="Record a study answer",
)
def record_study_answer(
    session_id: int,
    payload: StudyAnswerCreate,
    service: StudyServiceDep,
) -> StudyAnswerRead:
    """Record one answer in a study session."""
    return service.add_answer(session_id, payload)


@router.post(
    "/{session_id}/complete",
    response_model=StudySessionCompleteResponse,
    summary="Complete a study session",
)
def complete_study_session(
    session_id: int,
    payload: StudySessionComplete,
    service: StudyServiceDep,
) -> StudySessionCompleteResponse:
    """Complete a session and update version progress."""
    return service.complete_session(session_id, payload)
