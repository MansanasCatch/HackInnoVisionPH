"""ORM models. Import every model here so Alembic autogenerate can discover it."""

from app.models.project import Project, ProjectStatus

__all__ = ["Project", "ProjectStatus"]
