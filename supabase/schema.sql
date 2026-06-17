-- Run this in the Supabase SQL editor to create the starter schema.

create table if not exists public.dcf_models (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  ticker text,
  assumptions jsonb not null default '{}'::jsonb,
  client text,
  currency varchar(3) not null default 'EUR',
  valuation_date date,
  reporting_language varchar(10) not null default 'de',
  status varchar(50) not null default 'draft',
  created_by uuid references public.profiles (id) on delete set null,
  team_name text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists idx_dcf_models_status on public.dcf_models (status);
create index if not exists idx_dcf_models_name on public.dcf_models (name);
create index if not exists idx_dcf_models_client on public.dcf_models (client);
create index if not exists idx_dcf_models_created_at on public.dcf_models (created_at);
create index if not exists idx_dcf_models_updated_at on public.dcf_models (updated_at);

create table if not exists public.project_assets (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references public.dcf_models (id) on delete cascade,
  name text not null,
  created_at timestamptz not null default now()
);

create index if not exists idx_project_assets_project on public.project_assets (project_id);

create table if not exists public.valuation_runs (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references public.dcf_models (id) on delete cascade,
  run_number integer not null,
  status varchar(50) not null default 'pending',
  created_at timestamptz not null default now(),
  completed_at timestamptz,
  constraint uq_valuation_run_project_number unique (project_id, run_number)
);

create index if not exists idx_valuation_runs_project_created on public.valuation_runs (project_id, created_at desc);
create index if not exists idx_valuation_runs_status on public.valuation_runs (status);

create table if not exists public.project_reports (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references public.dcf_models (id) on delete cascade,
  format varchar(20) not null default 'pdf',
  generated_at timestamptz not null default now()
);

create index if not exists idx_project_reports_generated_at on public.project_reports (generated_at);
create index if not exists idx_project_reports_project on public.project_reports (project_id);

alter table public.dcf_models enable row level security;

create policy "Allow public read access"
  on public.dcf_models
  for select
  using (true);
