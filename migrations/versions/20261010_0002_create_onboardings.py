"""Create onboardings table.

Revision ID: 0002_create_onboardings
Revises: 0001_create_projects
Create Date: 2026-10-10 00:00:00+00:00

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002_create_onboardings"
down_revision: str | None = "0001_create_projects"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "onboardings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("username", sa.String(length=100), nullable=False),
        sa.Column("interests", sa.JSON(), nullable=False),
        sa.Column("age", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_onboardings")),
    )
    op.create_index(op.f("ix_onboardings_username"), "onboardings", ["username"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_onboardings_username"), table_name="onboardings")
    op.drop_table("onboardings")
