"""Create learning resources, versions, study sessions, and progress records.

Revision ID: 0004_create_learning_resources
Revises: 0003_create_device_specs
Create Date: 2026-10-10 02:30:00+00:00

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0004_create_learning_resources"
down_revision: str | None = "0003_create_device_specs"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "learning_resources",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("onboarding_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("subject", sa.String(length=100), nullable=False),
        sa.Column("source_label", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["onboarding_id"],
            ["onboardings.id"],
            name=op.f("fk_learning_resources_onboarding_id_onboardings"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_learning_resources")),
    )
    op.create_index(
        op.f("ix_learning_resources_onboarding_id"),
        "learning_resources",
        ["onboarding_id"],
        unique=False,
    )

    op.create_table(
        "learning_resource_versions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("learning_resource_id", sa.Integer(), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("content", sa.JSON(), nullable=False),
        sa.Column("resource_types", sa.JSON(), nullable=False),
        sa.Column("topics", sa.JSON(), nullable=False),
        sa.Column("is_current", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["learning_resource_id"],
            ["learning_resources.id"],
            name=op.f("fk_learning_resource_versions_learning_resource_id_learning_resources"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_learning_resource_versions")),
        sa.UniqueConstraint(
            "learning_resource_id",
            "version_number",
            name="uq_learning_resource_versions_resource_version",
        ),
    )
    op.create_index(
        op.f("ix_learning_resource_versions_learning_resource_id"),
        "learning_resource_versions",
        ["learning_resource_id"],
        unique=False,
    )

    op.create_table(
        "study_sessions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("onboarding_id", sa.Integer(), nullable=False),
        sa.Column("resource_version_id", sa.Integer(), nullable=False),
        sa.Column("mode", sa.String(length=50), nullable=False),
        sa.Column("source", sa.String(length=50), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("score", sa.Integer(), nullable=True),
        sa.Column("total_items", sa.Integer(), nullable=False),
        sa.Column("correct_items", sa.Integer(), nullable=False),
        sa.Column("accuracy", sa.Float(), nullable=False),
        sa.Column("time_spent_seconds", sa.Integer(), nullable=False),
        sa.Column("first_time_for_version", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["onboarding_id"],
            ["onboardings.id"],
            name=op.f("fk_study_sessions_onboarding_id_onboardings"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["resource_version_id"],
            ["learning_resource_versions.id"],
            name=op.f("fk_study_sessions_resource_version_id_learning_resource_versions"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_study_sessions")),
    )
    op.create_index(
        op.f("ix_study_sessions_onboarding_id"),
        "study_sessions",
        ["onboarding_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_study_sessions_resource_version_id"),
        "study_sessions",
        ["resource_version_id"],
        unique=False,
    )

    op.create_table(
        "study_answers",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("study_session_id", sa.Integer(), nullable=False),
        sa.Column("question_id", sa.String(length=120), nullable=False),
        sa.Column("concept_id", sa.String(length=120), nullable=False),
        sa.Column("concept_name", sa.String(length=160), nullable=False),
        sa.Column("student_answer", sa.Text(), nullable=False),
        sa.Column("correct_answer", sa.Text(), nullable=False),
        sa.Column("is_correct", sa.Boolean(), nullable=False),
        sa.Column("time_taken_seconds", sa.Integer(), nullable=False),
        sa.Column("confidence", sa.Integer(), nullable=False),
        sa.Column("hints_used", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["study_session_id"],
            ["study_sessions.id"],
            name=op.f("fk_study_answers_study_session_id_study_sessions"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_study_answers")),
    )
    op.create_index(
        op.f("ix_study_answers_study_session_id"),
        "study_answers",
        ["study_session_id"],
        unique=False,
    )

    op.create_table(
        "user_version_progress",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("onboarding_id", sa.Integer(), nullable=False),
        sa.Column("resource_version_id", sa.Integer(), nullable=False),
        sa.Column("first_started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_studied_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("attempts_count", sa.Integer(), nullable=False),
        sa.Column("best_score", sa.Integer(), nullable=True),
        sa.Column("latest_score", sa.Integer(), nullable=True),
        sa.Column("latest_accuracy", sa.Float(), nullable=False),
        sa.Column("mastery_state", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["onboarding_id"],
            ["onboardings.id"],
            name=op.f("fk_user_version_progress_onboarding_id_onboardings"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["resource_version_id"],
            ["learning_resource_versions.id"],
            name=op.f("fk_user_version_progress_resource_version_id_learning_resource_versions"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_user_version_progress")),
        sa.UniqueConstraint(
            "onboarding_id",
            "resource_version_id",
            name="uq_user_version_progress_onboarding_version",
        ),
    )
    op.create_index(
        op.f("ix_user_version_progress_onboarding_id"),
        "user_version_progress",
        ["onboarding_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_user_version_progress_resource_version_id"),
        "user_version_progress",
        ["resource_version_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_user_version_progress_resource_version_id"),
        table_name="user_version_progress",
    )
    op.drop_index(
        op.f("ix_user_version_progress_onboarding_id"),
        table_name="user_version_progress",
    )
    op.drop_table("user_version_progress")
    op.drop_index(op.f("ix_study_answers_study_session_id"), table_name="study_answers")
    op.drop_table("study_answers")
    op.drop_index(op.f("ix_study_sessions_resource_version_id"), table_name="study_sessions")
    op.drop_index(op.f("ix_study_sessions_onboarding_id"), table_name="study_sessions")
    op.drop_table("study_sessions")
    op.drop_index(
        op.f("ix_learning_resource_versions_learning_resource_id"),
        table_name="learning_resource_versions",
    )
    op.drop_table("learning_resource_versions")
    op.drop_index(op.f("ix_learning_resources_onboarding_id"), table_name="learning_resources")
    op.drop_table("learning_resources")
