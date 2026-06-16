"""Portfolio manager role, assignments, and audit events table."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            DO $$ BEGIN
              ALTER TYPE public.app_role ADD VALUE 'portfolio_manager';
            EXCEPTION
              WHEN duplicate_object THEN NULL;
            END $$;
            """
        )
    )

    op.create_table(
        "project_portfolio_managers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("public.dcf_models.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("public.profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("assigned_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("public.profiles.id", ondelete="SET NULL"), nullable=True),
        sa.Column("assigned_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("project_id", "user_id", name="uq_project_portfolio_manager"),
        schema="public",
    )
    op.create_index("idx_project_portfolio_managers_project", "project_portfolio_managers", ["project_id"], schema="public")
    op.create_index("idx_project_portfolio_managers_user", "project_portfolio_managers", ["user_id"], schema="public")

    op.create_table(
        "audit_events",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("entity_type", sa.String(50), nullable=False),
        sa.Column("entity_id", sa.String(255), nullable=False),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column("field", sa.String(100), nullable=True),
        sa.Column("old_value", sa.Text(), nullable=True),
        sa.Column("new_value", sa.Text(), nullable=True),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("payload", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        schema="audit",
    )
    op.create_index("idx_audit_events_project_time", "audit_events", ["project_id", "created_at"], schema="audit")
    op.create_index("idx_audit_events_entity", "audit_events", ["entity_type", "entity_id"], schema="audit")


def downgrade() -> None:
    op.drop_index("idx_audit_events_entity", table_name="audit_events", schema="audit")
    op.drop_index("idx_audit_events_project_time", table_name="audit_events", schema="audit")
    op.drop_table("audit_events", schema="audit")
    op.drop_index("idx_project_portfolio_managers_user", table_name="project_portfolio_managers", schema="public")
    op.drop_index("idx_project_portfolio_managers_project", table_name="project_portfolio_managers", schema="public")
    op.drop_table("project_portfolio_managers", schema="public")
