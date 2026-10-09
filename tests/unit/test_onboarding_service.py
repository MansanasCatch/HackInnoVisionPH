"""Unit tests for OnboardingService business logic."""

from typing import Sequence

import pytest

from app.core.exceptions import ConflictError, NotFoundError
from app.db.base import utc_now
from app.models.onboarding import OnboardingProfile
from app.repositories.onboarding_repository import AbstractOnboardingRepository
from app.schemas.onboarding import OnboardingCreate, OnboardingUpdate
from app.services.onboarding_service import OnboardingService


class FakeOnboardingRepository(AbstractOnboardingRepository):
    """In-memory fake repository for testing OnboardingService."""

    def __init__(self) -> None:
        self._items: dict[int, OnboardingProfile] = {}
        self._next_id = 1

    def add(self, profile: OnboardingProfile) -> OnboardingProfile:
        now = utc_now()
        profile.id = self._next_id
        self._next_id += 1
        profile.created_at = now
        profile.updated_at = now
        self._items[profile.id] = profile
        return profile

    def get(self, profile_id: int) -> OnboardingProfile | None:
        return self._items.get(profile_id)

    def get_by_username(self, username: str) -> OnboardingProfile | None:
        for profile in self._items.values():
            if profile.username.lower() == username.lower():
                return profile
        return None

    def list(self, *, limit: int = 50, offset: int = 0) -> Sequence[OnboardingProfile]:
        return list(self._items.values())[offset : offset + limit]

    def update(self, profile: OnboardingProfile) -> OnboardingProfile:
        profile.updated_at = utc_now()
        self._items[profile.id] = profile
        return profile


@pytest.fixture
def service() -> OnboardingService:
    return OnboardingService(FakeOnboardingRepository())


def test_create_onboarding_profile(service: OnboardingService) -> None:
    payload = OnboardingCreate(
        username="Amara Mensah",
        interests=["Biology", "English", "History"],
        age=20,
    )
    result = service.create_profile(payload)
    assert result.id == 1
    assert result.username == "Amara Mensah"
    assert result.interests == ["Biology", "English", "History"]
    assert result.age == 20


def test_create_duplicate_username_raises_conflict(service: OnboardingService) -> None:
    payload = OnboardingCreate(
        username="Amara Mensah",
        interests=["Biology"],
        age=20,
    )
    service.create_profile(payload)
    with pytest.raises(ConflictError):
        service.create_profile(payload)


def test_get_nonexistent_profile_raises_not_found(service: OnboardingService) -> None:
    with pytest.raises(NotFoundError):
        service.get_profile(999)


def test_update_onboarding_profile(service: OnboardingService) -> None:
    created = service.create_profile(
        OnboardingCreate(username="Amara Mensah", interests=["Biology"], age=20)
    )
    updated = service.update_profile(
        created.id, OnboardingUpdate(interests=["Biology", "Chemistry"], age=21)
    )
    assert updated.interests == ["Biology", "Chemistry"]
    assert updated.age == 21
