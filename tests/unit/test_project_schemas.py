"""Unit tests for request validation schemas."""

import pytest
from pydantic import ValidationError

from app.models.project import ProjectStatus
from app.schemas.project import ProjectCreate


def test_strips_whitespace() -> None:
    project = ProjectCreate(name="  AgriSense  ", team_name="  Palay ")

    assert project.name == "AgriSense"
    assert project.team_name == "Palay"


def test_default_status_is_idea() -> None:
    assert ProjectCreate(name="AgriSense", team_name="Palay").status is ProjectStatus.IDEA


@pytest.mark.parametrize(
    "payload",
    [
        {"name": "ab", "team_name": "Palay"},
        {"name": "AgriSense", "team_name": "P"},
        {"name": "AgriSense", "team_name": "Palay", "status": "unknown"},
    ],
)
def test_rejects_invalid_payloads(payload: dict[str, str]) -> None:
    with pytest.raises(ValidationError):
        ProjectCreate.model_validate(payload)
