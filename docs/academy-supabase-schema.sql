create table if not exists public.academy_students (
  id text primary key,
  email text,
  "displayName" text,
  "learningLanguage" text not null,
  level text not null,
  streak integer not null default 0,
  "completedLessons" integer not null default 0,
  "lastActiveAt" timestamptz,
  "createdAt" timestamptz not null default now(),
  "accessStatus" text not null default 'active'
);

create table if not exists public.academy_events (
  id uuid primary key,
  "studentId" text not null references public.academy_students(id) on delete cascade,
  type text not null,
  language text,
  level text,
  "lessonId" text,
  "createdAt" timestamptz not null default now()
);

create index if not exists academy_events_student_created_idx on public.academy_events ("studentId", "createdAt" desc);
create index if not exists academy_events_type_created_idx on public.academy_events (type, "createdAt" desc);

-- Server-only access is expected through AIRA_SUPABASE_SERVICE_ROLE_KEY.
-- Do not expose the service-role key to client-side code.
