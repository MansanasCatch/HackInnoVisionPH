"""``Project`` ORM model — a hackathon team's project submission."""

from enum import StrEnum

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class ProjectStatus(StrEnum):
    """Lifecycle stages of a hackathon project."""

    IDEA = "idea"
    BUILDING = "building"
    SUBMITTED = "submitted"


class Project(TimestampMixin, Base):
    """A project being built during the hackathon."""

    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    team_name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    tech_stack: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), default=ProjectStatus.IDEA.value, index=True, nullable=False
    )

    def __repr__(self) -> str:
        return f"<Project id={self.id} name={self.name!r} status={self.status}>"
