"""Pydantic schemas for onboarding validation and response serialization."""

from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

UsernameStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]


class OnboardingBase(BaseModel):
    """Common onboarding profile fields."""

    username: UsernameStr = Field(description="Display username / full name")
    interests: list[str] = Field(
        default_factory=list,
        description="List of selected interest topics (e.g., Biology, Chemistry, Physics)",
    )
    age: int = Field(ge=1, le=150, description="User age in years")


class OnboardingCreate(OnboardingBase):
    """Payload sent by clients when submitting onboarding info."""

    pass


class OnboardingUpdate(BaseModel):
    """Payload sent by clients when modifying onboarding info."""

    username: UsernameStr | None = Field(default=None, description="Updated username")
    interests: list[str] | None = Field(default=None, description="Updated list of interests")
    age: int | None = Field(default=None, ge=1, le=150, description="Updated user age")


class OnboardingRead(OnboardingBase):
    """Schema returned by endpoints."""

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
