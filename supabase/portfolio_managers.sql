-- Portfolio Manager role and project assignments (run after auth.sql and schema.sql)

do $$ begin
  alter type public.app_role add value 'portfolio_manager';
exception
  when duplicate_object then null;
end $$;

create table if not exists public.project_portfolio_managers (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references public.dcf_models (id) on delete cascade,
  user_id uuid not null references public.profiles (id) on delete cascade,
  assigned_by uuid references public.profiles (id) on delete set null,
  assigned_at timestamptz not null default now(),
  constraint uq_project_portfolio_manager unique (project_id, user_id)
);

create index if not exists idx_project_portfolio_managers_project
  on public.project_portfolio_managers (project_id);

create index if not exists idx_project_portfolio_managers_user
  on public.project_portfolio_managers (user_id);

alter table public.project_portfolio_managers enable row level security;

drop policy if exists "Admins manage portfolio manager assignments" on public.project_portfolio_managers;
create policy "Admins manage portfolio manager assignments"
  on public.project_portfolio_managers
  for all
  using (public.is_admin())
  with check (public.is_admin());

drop policy if exists "Portfolio managers read own assignments" on public.project_portfolio_managers;
create policy "Portfolio managers read own assignments"
  on public.project_portfolio_managers
  for select
  using (auth.uid() = user_id);

create table if not exists audit.audit_events (
  id bigint generated always as identity primary key,
  project_id uuid,
  entity_type varchar(50) not null,
  entity_id varchar(255) not null,
  action varchar(50) not null,
  field varchar(100),
  old_value text,
  new_value text,
  reason text,
  user_id uuid,
  payload jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create index if not exists idx_audit_events_project_time
  on audit.audit_events (project_id, created_at desc);

create index if not exists idx_audit_events_entity
  on audit.audit_events (entity_type, entity_id);
