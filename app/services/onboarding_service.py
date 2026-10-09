"""Use cases for managing user onboarding profiles."""

from app.core.exceptions import ConflictError, NotFoundError
from app.models.onboarding import OnboardingProfile
from app.repositories.onboarding_repository import AbstractOnboardingRepository
from app.schemas.onboarding import OnboardingCreate, OnboardingRead, OnboardingUpdate


class OnboardingService:
    """Orchestrates onboarding rules and persistence."""

    def __init__(self, repository: AbstractOnboardingRepository) -> None:
        self._repository = repository

    def create_profile(self, payload: OnboardingCreate) -> OnboardingRead:
        """Create a new onboarding profile with username, interests, and age."""
        existing = self._repository.get_by_username(payload.username)
        if existing is not None:
            raise ConflictError(f"Onboarding profile for '{payload.username}' already exists.")

        profile = OnboardingProfile(
            username=payload.username,
            interests=payload.interests,
            age=payload.age,
        )
        saved = self._repository.add(profile)
        return OnboardingRead.model_validate(saved)

    def get_profile(self, profile_id: int) -> OnboardingRead:
        """Fetch an onboarding profile by ID."""
        profile = self._repository.get(profile_id)
        if profile is None:
            raise NotFoundError(f"Onboarding profile with ID {profile_id} was not found.")
        return OnboardingRead.model_validate(profile)

    def get_profile_by_username(self, username: str) -> OnboardingRead:
        """Fetch an onboarding profile by username."""
        profile = self._repository.get_by_username(username)
        if profile is None:
            raise NotFoundError(f"Onboarding profile for '{username}' was not found.")
        return OnboardingRead.model_validate(profile)

    def list_profiles(self, *, limit: int = 50, offset: int = 0) -> list[OnboardingRead]:
        """List onboarding profiles with pagination."""
        profiles = self._repository.list(limit=limit, offset=offset)
        return [OnboardingRead.model_validate(p) for p in profiles]

    def update_profile(self, profile_id: int, payload: OnboardingUpdate) -> OnboardingRead:
        """Update an existing onboarding profile."""
        profile = self._repository.get(profile_id)
        if profile is None:
            raise NotFoundError(f"Onboarding profile with ID {profile_id} was not found.")

        if payload.username is not None and payload.username.lower() != profile.username.lower():
            existing = self._repository.get_by_username(payload.username)
            if existing is not None and existing.id != profile_id:
                raise ConflictError(f"Username '{payload.username}' is already taken.")
            profile.username = payload.username

        if payload.interests is not None:
            profile.interests = payload.interests

        if payload.age is not None:
            profile.age = payload.age

        updated = self._repository.update(profile)
        return OnboardingRead.model_validate(updated)
