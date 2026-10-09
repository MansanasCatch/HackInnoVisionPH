"""Endpoints for user onboarding account setup."""

from typing import Annotated

from fastapi import APIRouter, Query, status

from app.api.deps import OnboardingServiceDep
from app.schemas.onboarding import OnboardingCreate, OnboardingRead, OnboardingUpdate

router = APIRouter(prefix="/onboarding", tags=["Onboarding"])


@router.post(
    "",
    response_model=OnboardingRead,
    status_code=status.HTTP_201_CREATED,
    summary="Save onboarding account setup",
    description="Save username, list of interests, and age for onboarding.",
)
def create_onboarding_profile(
    payload: OnboardingCreate,
    service: OnboardingServiceDep,
) -> OnboardingRead:
    """Create and save a new onboarding profile."""
    return service.create_profile(payload)


@router.get(
    "",
    response_model=list[OnboardingRead],
    summary="List all onboarding profiles",
    description="Fetch saved onboarding profiles with optional pagination.",
)
def list_onboarding_profiles(
    service: OnboardingServiceDep,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[OnboardingRead]:
    """List onboarding profiles."""
    return service.list_profiles(limit=limit, offset=offset)


@router.get(
    "/{profile_id}",
    response_model=OnboardingRead,
    summary="Get onboarding profile by ID",
    description="Fetch a specific onboarding profile using its unique ID.",
)
def get_onboarding_profile_by_id(
    profile_id: int,
    service: OnboardingServiceDep,
) -> OnboardingRead:
    """Get an onboarding profile by ID."""
    return service.get_profile(profile_id)


@router.get(
    "/user/{username}",
    response_model=OnboardingRead,
    summary="Get onboarding profile by Username",
    description="Fetch a specific onboarding profile using the username.",
)
def get_onboarding_profile_by_username(
    username: str,
    service: OnboardingServiceDep,
) -> OnboardingRead:
    """Get an onboarding profile by username."""
    return service.get_profile_by_username(username)


@router.put(
    "/{profile_id}",
    response_model=OnboardingRead,
    summary="Update onboarding profile",
    description="Update username, interests, or age for an existing onboarding profile.",
)
def update_onboarding_profile(
    profile_id: int,
    payload: OnboardingUpdate,
    service: OnboardingServiceDep,
) -> OnboardingRead:
    """Update an onboarding profile."""
    return service.update_profile(profile_id, payload)
