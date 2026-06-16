"""Initial schema: lifecycle schemas and dcf_models table."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

LIFECYCLE_SCHEMAS = ("source", "extracted", "approved", "calculated", "audit")


def upgrade() -> None:
    for schema in LIFECYCLE_SCHEMAS:
        op.execute(sa.text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))

    op.create_table(
        "dcf_models",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("ticker", sa.Text(), nullable=True),
        sa.Column("assumptions", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        schema="public",
    )

    op.execute(
        sa.text(
            """
            ALTER TABLE public.dcf_models ENABLE ROW LEVEL SECURITY;
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_policies
                    WHERE schemaname = 'public'
                      AND tablename = 'dcf_models'
                      AND policyname = 'Allow public read access'
                ) THEN
                    CREATE POLICY "Allow public read access"
                        ON public.dcf_models
                        FOR SELECT
                        USING (true);
                END IF;
            END $$;
            """
        )
    )


def downgrade() -> None:
    op.drop_table("dcf_models", schema="public")
    for schema in reversed(LIFECYCLE_SCHEMAS):
        op.execute(sa.text(f"DROP SCHEMA IF EXISTS {schema} CASCADE"))
