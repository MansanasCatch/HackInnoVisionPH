"""Create device_specs table.

Revision ID: 0003_create_device_specs
Revises: 0002_create_onboardings
Create Date: 2026-10-10 01:00:00+00:00

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003_create_device_specs"
down_revision: str | None = "0002_create_onboardings"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "device_specs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("onboarding_id", sa.Integer(), nullable=False),
        sa.Column("ram_gb", sa.Float(), nullable=False),
        sa.Column("gpu_name", sa.String(length=120), nullable=True),
        sa.Column("vram_gb", sa.Float(), nullable=False),
        sa.Column("cpu_cores", sa.Integer(), nullable=False),
        sa.Column("storage_free_gb", sa.Float(), nullable=False),
        sa.Column("os_name", sa.String(length=50), nullable=False),
        sa.Column("selected_model", sa.String(length=100), nullable=False),
        sa.Column("pull_status", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["onboarding_id"],
            ["onboardings.id"],
            name=op.f("fk_device_specs_onboarding_id_onboardings"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_device_specs")),
    )
    op.create_index(
        op.f("ix_device_specs_onboarding_id"), "device_specs", ["onboarding_id"], unique=True
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_device_specs_onboarding_id"), table_name="device_specs")
    op.drop_table("device_specs")
