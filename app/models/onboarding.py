"""ORM model for user onboarding profiles."""

from typing import TYPE_CHECKING

from sqlalchemy import JSON, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.device import DeviceSpecs
    from app.models.learning_resource import LearningResource
    from app.models.study import (
        ArchivedVersionAnalytics,
        StudySession,
        UserVersionProgress,
    )


class OnboardingProfile(Base, TimestampMixin):
    """ORM representation of a user's onboarding preferences and info."""

    __tablename__ = "onboardings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    interests: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)

    device_specs: Mapped["DeviceSpecs | None"] = relationship(
        "DeviceSpecs", back_populates="onboarding", uselist=False, cascade="all, delete-orphan"
    )
    learning_resources: Mapped[list["LearningResource"]] = relationship(
        "LearningResource", cascade="all, delete-orphan", passive_deletes=True
    )
    study_sessions: Mapped[list["StudySession"]] = relationship(
        "StudySession", cascade="all, delete-orphan", passive_deletes=True
    )
    version_progress: Mapped[list["UserVersionProgress"]] = relationship(
        "UserVersionProgress", cascade="all, delete-orphan", passive_deletes=True
    )
    archived_analytics: Mapped[list["ArchivedVersionAnalytics"]] = relationship(
        "ArchivedVersionAnalytics", cascade="all, delete-orphan", passive_deletes=True
    )

    def __repr__(self) -> str:
        return f"<OnboardingProfile id={self.id} username={self.username!r} age={self.age}>"
