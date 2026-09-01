-- ============================================================
-- Family Beacon
-- Migration: 018_parent_telegram_id_on_profile
-- Database: Supabase PostgreSQL
--
-- Store parent Telegram ID in profiles during Auth registration.
-- Telegram ID is passed through Supabase Auth user metadata.
-- SQLite is NOT used.
-- ============================================================

create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
    insert into public.profiles (
        id,
        display_name,
        telegram_id
    )
    values (
        new.id,
        coalesce(
            new.raw_user_meta_data ->> 'full_name',
            new.raw_user_meta_data ->> 'name'
        ),
        nullif(
            new.raw_user_meta_data ->> 'telegram_id',
            ''
        )::bigint
    );

    return new;
end;
$$;
