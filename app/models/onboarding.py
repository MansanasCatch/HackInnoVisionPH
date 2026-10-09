"""ORM model for user onboarding profiles."""

from typing import Any

from sqlalchemy import JSON, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class OnboardingProfile(Base, TimestampMixin):
    """ORM representation of a user's onboarding preferences and info."""

    __tablename__ = "onboardings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    interests: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)

    def __repr__(self) -> str:
        return f"<OnboardingProfile id={self.id} username={self.username!r} age={self.age}>"
