"""ORM model for user onboarding profiles."""

from typing import TYPE_CHECKING

from sqlalchemy import JSON, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.device import DeviceSpecs


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

    def __repr__(self) -> str:
        return f"<OnboardingProfile id={self.id} username={self.username!r} age={self.age}>"
