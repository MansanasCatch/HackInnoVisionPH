"""ORM records for versioned learning resources."""

from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, Boolean, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.study import StudySession, UserVersionProgress


class LearningResource(Base, TimestampMixin):
    """A learner-owned set of generated study materials."""

    __tablename__ = "learning_resources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    onboarding_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("onboardings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    subject: Mapped[str] = mapped_column(String(100), default="", nullable=False)
    source_label: Mapped[str] = mapped_column(String(255), default="", nullable=False)

    versions: Mapped[list["LearningResourceVersion"]] = relationship(
        "LearningResourceVersion",
        back_populates="learning_resource",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<LearningResource id={self.id} title={self.title!r}>"


class LearningResourceVersion(Base, TimestampMixin):
    """One generated version of a learning resource record."""

    __tablename__ = "learning_resource_versions"
    __table_args__ = (
        UniqueConstraint(
            "learning_resource_id",
            "version_number",
            name="uq_learning_resource_versions_resource_version",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    learning_resource_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("learning_resources.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    summary: Mapped[str] = mapped_column(Text, default="", nullable=False)
    content: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    resource_types: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    topics: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    is_current: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    learning_resource: Mapped[LearningResource] = relationship(
        "LearningResource",
        back_populates="versions",
    )
    study_sessions: Mapped[list["StudySession"]] = relationship(
        "StudySession",
        back_populates="resource_version",
        cascade="all, delete-orphan",
    )
    progress_records: Mapped[list["UserVersionProgress"]] = relationship(
        "UserVersionProgress",
        back_populates="resource_version",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            "<LearningResourceVersion "
            f"id={self.id} resource_id={self.learning_resource_id} "
            f"version={self.version_number}>"
        )
