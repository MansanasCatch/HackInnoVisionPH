"""Persistence for :class:`~app.models.project.Project`.

``AbstractProjectRepository`` is the port the service depends on;
``SqlAlchemyProjectRepository`` is the concrete adapter. Tests can swap in an
in-memory fake without touching business logic.
"""

from abc import ABC, abstractmethod
from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.project import Project


class AbstractProjectRepository(ABC):
    """Contract for project persistence."""

    @abstractmethod
    def list(
        self, *, status: str | None = None, limit: int = 50, offset: int = 0
    ) -> Sequence[Project]:
        """Return projects, newest first, optionally filtered by ``status``."""

    @abstractmethod
    def get(self, project_id: int) -> Project | None:
        """Return the project with ``project_id`` or ``None``."""

    @abstractmethod
    def get_by_name(self, name: str) -> Project | None:
        """Return the project named ``name`` (case-insensitive) or ``None``."""

    @abstractmethod
    def add(self, project: Project) -> Project:
        """Persist a new project and return it."""

    @abstractmethod
    def count_by_status(self) -> dict[str, int]:
        """Return a mapping of status -> number of projects."""


class SqlAlchemyProjectRepository(AbstractProjectRepository):
    """SQLAlchemy 2.0 implementation of :class:`AbstractProjectRepository`."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def list(
        self, *, status: str | None = None, limit: int = 50, offset: int = 0
    ) -> Sequence[Project]:
        stmt = select(Project).order_by(Project.created_at.desc(), Project.id.desc())
        if status is not None:
            stmt = stmt.where(Project.status == status)
        return self._session.scalars(stmt.limit(limit).offset(offset)).all()

    def get(self, project_id: int) -> Project | None:
        return self._session.get(Project, project_id)

    def get_by_name(self, name: str) -> Project | None:
        stmt = select(Project).where(func.lower(Project.name) == name.lower())
        return self._session.scalars(stmt).first()

    def add(self, project: Project) -> Project:
        self._session.add(project)
        self._session.commit()
        self._session.refresh(project)
        return project

    def count_by_status(self) -> dict[str, int]:
        stmt = select(Project.status, func.count(Project.id)).group_by(Project.status)
        rows = self._session.execute(stmt).all()
        return {str(row[0]): int(row[1]) for row in rows}
