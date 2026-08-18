-- Sprint 058: cross-device learner progress
-- Run in the Supabase SQL editor for the Academy project.

create table if not exists public.academy_progress (
  student_id text primary key,
  profile jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now()
);

create index if not exists academy_progress_updated_at_idx
  on public.academy_progress (updated_at desc);

alter table public.academy_progress enable row level security;

-- No public policies are created intentionally.
-- AIRA Academy accesses this table only through server-side routes using
-- AIRA_SUPABASE_SERVICE_ROLE_KEY. Student browser sessions never receive it.
