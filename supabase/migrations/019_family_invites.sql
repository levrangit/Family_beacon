-- ============================================================
-- Family Beacon
-- Migration: 019_family_invites
-- Database: Supabase PostgreSQL
--
-- Family invite codes v1:
-- - one-time use
-- - valid for 24 hours
-- - revocable
-- - only the hash of the code is stored
-- - created_by references the parent profile
-- - used_by references the profile that used the invite
-- ============================================================

create table if not exists public.family_invites (
    id uuid primary key default gen_random_uuid(),

    family_id uuid not null
        references public.families(id)
        on delete cascade,

    created_by uuid not null
        references public.profiles(id),

    code_hash text not null unique,

    expires_at timestamptz not null,

    used_at timestamptz,

    used_by uuid
        references public.profiles(id),

    revoked_at timestamptz,

    created_at timestamptz not null default now()
);

create index if not exists family_invites_family_id_idx
    on public.family_invites(family_id);

create index if not exists family_invites_created_by_idx
    on public.family_invites(created_by);

create index if not exists family_invites_used_by_idx
    on public.family_invites(used_by);

create index if not exists family_invites_expires_at_idx
    on public.family_invites(expires_at);

alter table public.family_invites enable row level security;
