"""Integration tests for the SQLAlchemy project repository."""

from sqlalchemy.orm import Session

from app.models.project import Project, ProjectStatus
from app.repositories.project_repository import SqlAlchemyProjectRepository


def _make(name: str, status: ProjectStatus = ProjectStatus.IDEA) -> Project:
    return Project(name=name, team_name="Team", status=status.value)


def test_add_and_get(db_session: Session) -> None:
    repo = SqlAlchemyProjectRepository(db_session)

    saved = repo.add(_make("Alpha"))

    assert saved.id is not None
    assert repo.get(saved.id) is saved
    assert saved.created_at is not None


def test_get_by_name_is_case_insensitive(db_session: Session) -> None:
    repo = SqlAlchemyProjectRepository(db_session)
    repo.add(_make("JeepRoute"))

    assert repo.get_by_name("jeeproute") is not None
    assert repo.get_by_name("missing") is None


def test_list_filters_and_counts(db_session: Session) -> None:
    repo = SqlAlchemyProjectRepository(db_session)
    repo.add(_make("Alpha", ProjectStatus.BUILDING))
    repo.add(_make("Bravo", ProjectStatus.BUILDING))
    repo.add(_make("Charlie", ProjectStatus.SUBMITTED))

    building = repo.list(status=ProjectStatus.BUILDING.value)

    assert {p.name for p in building} == {"Alpha", "Bravo"}
    assert repo.count_by_status() == {"building": 2, "submitted": 1}
