"""Idempotent repair: ensure project dashboard tables exist."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            CREATE TABLE IF NOT EXISTS public.dcf_models (
              id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
              name text NOT NULL,
              ticker text,
              assumptions jsonb NOT NULL DEFAULT '{}'::jsonb,
              client text,
              currency varchar(3) NOT NULL DEFAULT 'EUR',
              valuation_date date,
              reporting_language varchar(10) NOT NULL DEFAULT 'de',
              status varchar(50) NOT NULL DEFAULT 'draft',
              created_by uuid REFERENCES public.profiles (id) ON DELETE SET NULL,
              team_name text,
              created_at timestamptz NOT NULL DEFAULT now(),
              updated_at timestamptz NOT NULL DEFAULT now()
            );

            ALTER TABLE public.dcf_models ADD COLUMN IF NOT EXISTS client text;
            ALTER TABLE public.dcf_models ADD COLUMN IF NOT EXISTS currency varchar(3) NOT NULL DEFAULT 'EUR';
            ALTER TABLE public.dcf_models ADD COLUMN IF NOT EXISTS valuation_date date;
            ALTER TABLE public.dcf_models ADD COLUMN IF NOT EXISTS reporting_language varchar(10) NOT NULL DEFAULT 'de';
            ALTER TABLE public.dcf_models ADD COLUMN IF NOT EXISTS status varchar(50) NOT NULL DEFAULT 'draft';
            ALTER TABLE public.dcf_models ADD COLUMN IF NOT EXISTS created_by uuid;
            ALTER TABLE public.dcf_models ADD COLUMN IF NOT EXISTS team_name text;

            CREATE INDEX IF NOT EXISTS idx_dcf_models_status ON public.dcf_models (status);
            CREATE INDEX IF NOT EXISTS idx_dcf_models_name ON public.dcf_models (name);
            CREATE INDEX IF NOT EXISTS idx_dcf_models_client ON public.dcf_models (client);
            CREATE INDEX IF NOT EXISTS idx_dcf_models_created_at ON public.dcf_models (created_at);
            CREATE INDEX IF NOT EXISTS idx_dcf_models_updated_at ON public.dcf_models (updated_at);

            CREATE TABLE IF NOT EXISTS public.project_assets (
              id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
              project_id uuid NOT NULL REFERENCES public.dcf_models (id) ON DELETE CASCADE,
              name text NOT NULL,
              created_at timestamptz NOT NULL DEFAULT now()
            );
            CREATE INDEX IF NOT EXISTS idx_project_assets_project ON public.project_assets (project_id);

            CREATE TABLE IF NOT EXISTS public.valuation_runs (
              id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
              project_id uuid NOT NULL REFERENCES public.dcf_models (id) ON DELETE CASCADE,
              run_number integer NOT NULL,
              status varchar(50) NOT NULL DEFAULT 'pending',
              created_at timestamptz NOT NULL DEFAULT now(),
              completed_at timestamptz,
              CONSTRAINT uq_valuation_run_project_number UNIQUE (project_id, run_number)
            );
            CREATE INDEX IF NOT EXISTS idx_valuation_runs_project_created
              ON public.valuation_runs (project_id, created_at DESC);
            CREATE INDEX IF NOT EXISTS idx_valuation_runs_status ON public.valuation_runs (status);

            CREATE TABLE IF NOT EXISTS public.project_reports (
              id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
              project_id uuid NOT NULL REFERENCES public.dcf_models (id) ON DELETE CASCADE,
              format varchar(20) NOT NULL DEFAULT 'pdf',
              generated_at timestamptz NOT NULL DEFAULT now()
            );
            CREATE INDEX IF NOT EXISTS idx_project_reports_generated_at ON public.project_reports (generated_at);
            CREATE INDEX IF NOT EXISTS idx_project_reports_project ON public.project_reports (project_id);
            """
        )
    )


def downgrade() -> None:
    pass
