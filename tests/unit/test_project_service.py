"""Unit tests for :class:`app.services.project_service.ProjectService`.

The service is exercised against an in-memory fake repository, proving the
business rules are independent of SQLAlchemy and FastAPI.
"""

from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any

import pytest

from app.core.exceptions import ConflictError, NotFoundError
from app.models.project import Project, ProjectStatus
from app.repositories.project_repository import AbstractProjectRepository
from app.schemas.project import ProjectCreate
from app.services.project_service import ProjectService


class FakeProjectRepository(AbstractProjectRepository):
    """Dictionary-backed repository for unit tests."""

    def __init__(self) -> None:
        self._items: dict[int, Project] = {}
        self._next_id = 1

    def list(
        self, *, status: str | None = None, limit: int = 50, offset: int = 0
    ) -> Sequence[Project]:
        items = [p for p in self._items.values() if status is None or p.status == status]
        items.sort(key=lambda p: p.id, reverse=True)
        return items[offset : offset + limit]

    def get(self, project_id: int) -> Project | None:
        return self._items.get(project_id)

    def get_by_name(self, name: str) -> Project | None:
        return next((p for p in self._items.values() if p.name.lower() == name.lower()), None)

    def add(self, project: Project) -> Project:
        now = datetime.now(UTC)
        project.id = self._next_id
        project.created_at = now
        project.updated_at = now
        self._items[project.id] = project
        self._next_id += 1
        return project

    def count_by_status(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for project in self._items.values():
            counts[project.status] = counts.get(project.status, 0) + 1
        return counts


@pytest.fixture
def service() -> ProjectService:
    return ProjectService(FakeProjectRepository())


def _payload(name: str = "SmartBayanihan", **overrides: Any) -> ProjectCreate:
    data: dict[str, Any] = {"name": name, "team_name": "Team Kalinga", **overrides}
    return ProjectCreate(**data)


class TestCreateProject:
    def test_creates_project_with_defaults(self, service: ProjectService) -> None:
        project = service.create_project(_payload())

        assert project.id == 1
        assert project.name == "SmartBayanihan"
        assert project.status is ProjectStatus.IDEA

    def test_rejects_duplicate_name_case_insensitive(self, service: ProjectService) -> None:
        service.create_project(_payload("JeepRoute"))

        with pytest.raises(ConflictError):
            service.create_project(_payload("jeeproute"))


class TestReadProjects:
    def test_get_missing_project_raises_not_found(self, service: ProjectService) -> None:
        with pytest.raises(NotFoundError):
            service.get_project(999)

    def test_list_filters_by_status(self, service: ProjectService) -> None:
        service.create_project(_payload("Alpha", status=ProjectStatus.BUILDING))
        service.create_project(_payload("Bravo", status=ProjectStatus.IDEA))

        result = service.list_projects(status=ProjectStatus.BUILDING)

        assert [p.name for p in result] == ["Alpha"]

    def test_stats_include_every_status(self, service: ProjectService) -> None:
        service.create_project(_payload("Alpha", status=ProjectStatus.SUBMITTED))

        stats = service.get_stats()

        assert stats.total == 1
        assert stats.by_status == {
            ProjectStatus.IDEA: 0,
            ProjectStatus.BUILDING: 0,
            ProjectStatus.SUBMITTED: 1,
        }
