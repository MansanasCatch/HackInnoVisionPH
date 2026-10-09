"""Request/response schemas for the ``Project`` resource."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.project import ProjectStatus


class _ProjectFields(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=3, max_length=120, examples=["SmartBayanihan"])
    team_name: str = Field(min_length=2, max_length=120, examples=["Team Kalinga"])
    description: str = Field(default="", max_length=1000)
    tech_stack: str = Field(default="", max_length=255, examples=["FastAPI, SQLite, JS"])
    status: ProjectStatus = ProjectStatus.IDEA


class ProjectCreate(_ProjectFields):
    """Payload used to register a new project."""


class ProjectRead(_ProjectFields):
    """Project representation returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class ProjectStats(BaseModel):
    """Aggregated project counts used by the dashboard."""

    total: int
    by_status: dict[ProjectStatus, int]
