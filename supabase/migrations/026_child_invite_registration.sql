-- ============================================================
-- Family Beacon
-- Migration: 026_child_invite_registration
-- Database: Supabase PostgreSQL
--
-- Register a Telegram child from a one-time family invite.
-- The operation is atomic: validate/consume invite and create
-- the child in one transaction.
--
-- Child registration does not create a profile or family_members
-- row. The child is represented by public.children and its
-- Telegram identity is stored in children.telegram_id.
-- ============================================================

alter table public.family_invites
    add column if not exists used_by_child uuid
        references public.children(id)
        on delete set null;

create index if not exists family_invites_used_by_child_idx
    on public.family_invites(used_by_child);

create or replace function public.register_child_by_invite(
    p_code_hash text,
    p_telegram_id bigint,
    p_child_name text
)
returns table (
    child_id uuid,
    family_id uuid,
    invite_id uuid
)
language plpgsql
security definer
set search_path = public
as $$
declare
    redeemed_invite_id uuid;
    redeemed_family_id uuid;
    new_child_id uuid;
begin
    if nullif(trim(p_code_hash), '') is null then
        raise exception 'Invite code hash is required';
    end if;

    if p_telegram_id is null then
        raise exception 'Telegram ID is required';
    end if;

    if p_telegram_id <= 0 then
        raise exception 'Telegram ID is invalid';
    end if;

    if nullif(trim(p_child_name), '') is null then
        raise exception 'Child name is required';
    end if;

    if exists (
        select 1
        from public.children
        where telegram_id = p_telegram_id
    ) then
        raise exception 'Telegram account is already registered as a child';
    end if;

    update public.family_invites
    set used_at = now()
    where family_invites.code_hash = p_code_hash
      and family_invites.used_at is null
      and family_invites.revoked_at is null
      and family_invites.expires_at > now()
    returning
        family_invites.id,
        family_invites.family_id
    into
        redeemed_invite_id,
        redeemed_family_id;

    if redeemed_invite_id is null then
        raise exception 'Invite is invalid, expired, revoked, or already used';
    end if;

    insert into public.children (
        family_id,
        name,
        telegram_id
    )
    values (
        redeemed_family_id,
        trim(p_child_name),
        p_telegram_id
    )
    returning id into new_child_id;

    update public.family_invites
    set used_by_child = new_child_id
    where id = redeemed_invite_id;

    return query
    select
        new_child_id,
        redeemed_family_id,
        redeemed_invite_id;
end;
$$;

revoke all on function public.register_child_by_invite(text, bigint, text)
from public;

grant execute on function public.register_child_by_invite(text, bigint, text)
to service_role;
