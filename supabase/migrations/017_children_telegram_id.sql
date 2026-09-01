-- ============================================================
-- Family Beacon
-- Migration: 017_children_telegram_id
-- Database: Supabase PostgreSQL
--
-- Add Telegram identity to children.
-- SQLite is NOT used.
-- ============================================================

alter table public.children
    add column if not exists telegram_id bigint;

create unique index if not exists children_telegram_id_unique_idx
    on public.children (telegram_id)
    where telegram_id is not null;
