-- Run this in the Supabase SQL editor to create the starter schema.

create table if not exists public.dcf_models (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  ticker text,
  assumptions jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

alter table public.dcf_models enable row level security;

create policy "Allow public read access"
  on public.dcf_models
  for select
  using (true);
