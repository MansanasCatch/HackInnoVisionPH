"""Create projects table and seed sample hackathon projects.

Revision ID: 0001_create_projects
Revises:
Create Date: 2026-10-04 00:00:00+00:00

"""

from collections.abc import Sequence
from datetime import UTC, datetime

import sqlalchemy as sa
from alembic import op

revision: str = "0001_create_projects"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    projects = op.create_table(
        "projects",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("team_name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("tech_stack", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_projects")),
    )
    op.create_index(op.f("ix_projects_name"), "projects", ["name"], unique=True)
    op.create_index(op.f("ix_projects_status"), "projects", ["status"], unique=False)

    now = datetime.now(UTC)
    op.bulk_insert(
        projects,
        [
            {
                "name": "SmartBayanihan",
                "team_name": "Team Kalinga",
                "description": "Community volunteer matching for disaster response.",
                "tech_stack": "FastAPI, SQLite, Vanilla JS",
                "status": "building",
                "created_at": now,
                "updated_at": now,
            },
            {
                "name": "AgriSense PH",
                "team_name": "Team Palay",
                "description": "IoT soil monitoring with SMS alerts for rice farmers.",
                "tech_stack": "Python, MQTT, Twilio",
                "status": "idea",
                "created_at": now,
                "updated_at": now,
            },
            {
                "name": "JeepRoute",
                "team_name": "Team Biyahe",
                "description": "Crowdsourced jeepney route finder for commuters.",
                "tech_stack": "FastAPI, Leaflet, PostgreSQL",
                "status": "submitted",
                "created_at": now,
                "updated_at": now,
            },
        ],
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_projects_status"), table_name="projects")
    op.drop_index(op.f("ix_projects_name"), table_name="projects")
    op.drop_table("projects")
