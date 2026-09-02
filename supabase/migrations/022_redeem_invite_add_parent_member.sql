-- ============================================================
-- Family Beacon
-- Migration: 022_redeem_invite_add_parent_member
-- Database: Supabase PostgreSQL
--
-- Fix redeem flow:
-- - redeeming an invite also adds the authenticated user to the family
-- - the new member is added as a parent
-- - invite consumption and membership creation remain atomic
-- ============================================================

create or replace function public.redeem_family_invite(
    p_code_hash text
)
returns table (
    invite_id uuid,
    family_id uuid
)
language plpgsql
security definer
set search_path = public
as $$
declare
    redeemed_invite_id uuid;
    redeemed_family_id uuid;
begin
    if auth.uid() is null then
        raise exception 'Authentication required';
    end if;

    if nullif(trim(p_code_hash), '') is null then
        raise exception 'Invite code hash is required';
    end if;

    update public.family_invites
    set
        used_at = now(),
        used_by = auth.uid()
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

    insert into public.family_members (
        family_id,
        profile_id,
        member_type
    )
    values (
        redeemed_family_id,
        auth.uid(),
        'parent'
    );

    return query
    select redeemed_invite_id, redeemed_family_id;
end;
$$;

revoke all on function public.redeem_family_invite(text)
from public;

grant execute on function public.redeem_family_invite(text)
to authenticated;
