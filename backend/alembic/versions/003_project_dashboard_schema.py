"""Extend dcf_models for portfolio dashboard and add supporting tables."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect
from sqlalchemy.dialects import postgresql

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _dcf_models_exists() -> bool:
    bind = op.get_bind()
    return "dcf_models" in inspect(bind).get_table_names(schema="public")


def upgrade() -> None:
    if not _dcf_models_exists():
        return
    op.add_column("dcf_models", sa.Column("client", sa.Text(), nullable=True), schema="public")
    op.add_column(
        "dcf_models",
        sa.Column("currency", sa.String(3), nullable=False, server_default="EUR"),
        schema="public",
    )
    op.add_column("dcf_models", sa.Column("valuation_date", sa.Date(), nullable=True), schema="public")
    op.add_column(
        "dcf_models",
        sa.Column("reporting_language", sa.String(10), nullable=False, server_default="de"),
        schema="public",
    )
    op.add_column(
        "dcf_models",
        sa.Column("status", sa.String(50), nullable=False, server_default="draft"),
        schema="public",
    )
    op.add_column(
        "dcf_models",
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        schema="public",
    )
    op.add_column("dcf_models", sa.Column("team_name", sa.Text(), nullable=True), schema="public")

    op.create_foreign_key(
        "fk_dcf_models_created_by",
        "dcf_models",
        "profiles",
        ["created_by"],
        ["id"],
        source_schema="public",
        referent_schema="public",
        ondelete="SET NULL",
    )

    op.create_index("idx_dcf_models_status", "dcf_models", ["status"], schema="public")
    op.create_index("idx_dcf_models_name", "dcf_models", ["name"], schema="public")
    op.create_index("idx_dcf_models_client", "dcf_models", ["client"], schema="public")
    op.create_index("idx_dcf_models_created_at", "dcf_models", ["created_at"], schema="public")
    op.create_index("idx_dcf_models_updated_at", "dcf_models", ["updated_at"], schema="public")

    op.create_table(
        "project_assets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "project_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("public.dcf_models.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        schema="public",
    )
    op.create_index("idx_project_assets_project", "project_assets", ["project_id"], schema="public")

    op.create_table(
        "valuation_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "project_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("public.dcf_models.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("run_number", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("project_id", "run_number", name="uq_valuation_run_project_number"),
        schema="public",
    )
    op.create_index(
        "idx_valuation_runs_project_created",
        "valuation_runs",
        ["project_id", "created_at"],
        schema="public",
    )
    op.create_index("idx_valuation_runs_status", "valuation_runs", ["status"], schema="public")

    op.create_table(
        "project_reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "project_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("public.dcf_models.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("format", sa.String(20), nullable=False, server_default="pdf"),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        schema="public",
    )
    op.create_index("idx_project_reports_generated_at", "project_reports", ["generated_at"], schema="public")
    op.create_index("idx_project_reports_project", "project_reports", ["project_id"], schema="public")


def downgrade() -> None:
    op.drop_index("idx_project_reports_project", table_name="project_reports", schema="public")
    op.drop_index("idx_project_reports_generated_at", table_name="project_reports", schema="public")
    op.drop_table("project_reports", schema="public")

    op.drop_index("idx_valuation_runs_status", table_name="valuation_runs", schema="public")
    op.drop_index("idx_valuation_runs_project_created", table_name="valuation_runs", schema="public")
    op.drop_table("valuation_runs", schema="public")

    op.drop_index("idx_project_assets_project", table_name="project_assets", schema="public")
    op.drop_table("project_assets", schema="public")

    op.drop_index("idx_dcf_models_updated_at", table_name="dcf_models", schema="public")
    op.drop_index("idx_dcf_models_created_at", table_name="dcf_models", schema="public")
    op.drop_index("idx_dcf_models_client", table_name="dcf_models", schema="public")
    op.drop_index("idx_dcf_models_name", table_name="dcf_models", schema="public")
    op.drop_index("idx_dcf_models_status", table_name="dcf_models", schema="public")

    op.drop_constraint("fk_dcf_models_created_by", "dcf_models", schema="public", type_="foreignkey")
    op.drop_column("dcf_models", "team_name", schema="public")
    op.drop_column("dcf_models", "created_by", schema="public")
    op.drop_column("dcf_models", "status", schema="public")
    op.drop_column("dcf_models", "reporting_language", schema="public")
    op.drop_column("dcf_models", "valuation_date", schema="public")
    op.drop_column("dcf_models", "currency", schema="public")
    op.drop_column("dcf_models", "client", schema="public")
