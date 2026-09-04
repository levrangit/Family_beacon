-- ============================================================
-- Family Beacon
-- Migration: 025_family_invites_code
-- Database: Supabase PostgreSQL
--
-- Store the original invitation code so a parent can view
-- previously created invitations from Telegram.
-- The existing code_hash remains the value used for redemption.
-- ============================================================

alter table public.family_invites
add column if not exists code text;

create index if not exists idx_family_invites_created_by_created_at
    on public.family_invites(created_by, created_at desc);
