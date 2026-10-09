"""Store compact analytics for pruned learning-resource versions.

Revision ID: 0005_archive_version_analytics
Revises: 0004_create_learning_resources
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0005_archive_version_analytics"
down_revision: str | None = "0004_create_learning_resources"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("study_sessions", sa.Column("generated_version_id", sa.Integer(), nullable=True))
    op.add_column(
        "study_sessions", sa.Column("archived_version_number", sa.Integer(), nullable=True)
    )
    op.create_table(
        "archived_version_analytics",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("learning_resource_id", sa.Integer(), nullable=False),
        sa.Column("onboarding_id", sa.Integer(), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("attempts_count", sa.Integer(), nullable=False),
        sa.Column("total_items", sa.Integer(), nullable=False),
        sa.Column("correct_items", sa.Integer(), nullable=False),
        sa.Column("total_time_seconds", sa.Integer(), nullable=False),
        sa.Column("best_score", sa.Integer(), nullable=True),
        sa.Column("latest_score", sa.Integer(), nullable=True),
        sa.Column("concept_stats", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["learning_resource_id"], ["learning_resources.id"],
            name=op.f("fk_archived_version_analytics_learning_resource_id_learning_resources"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["onboarding_id"], ["onboardings.id"],
            name=op.f("fk_archived_version_analytics_onboarding_id_onboardings"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_archived_version_analytics")),
        sa.UniqueConstraint(
            "learning_resource_id", "version_number", name="uq_archived_analytics_resource_version"
        ),
    )
    op.create_index(
        op.f("ix_archived_version_analytics_learning_resource_id"),
        "archived_version_analytics", ["learning_resource_id"], unique=False,
    )
    op.create_index(
        op.f("ix_archived_version_analytics_onboarding_id"),
        "archived_version_analytics", ["onboarding_id"], unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_archived_version_analytics_onboarding_id"),
        table_name="archived_version_analytics",
    )
    op.drop_index(
        op.f("ix_archived_version_analytics_learning_resource_id"),
        table_name="archived_version_analytics",
    )
    op.drop_table("archived_version_analytics")
    op.drop_column("study_sessions", "archived_version_number")
    op.drop_column("study_sessions", "generated_version_id")
