-- ============================================================
-- Family Beacon
-- Migration: 021_redeem_family_invite
-- Database: Supabase PostgreSQL
--
-- Redeem family invite:
-- - one-time use
-- - valid only before expires_at
-- - revoked invites are invalid
-- - used invites are invalid
-- - caller is recorded in used_by
-- - operation is atomic
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
begin
    if auth.uid() is null then
        raise exception 'Authentication required';
    end if;

    if nullif(trim(p_code_hash), '') is null then
        raise exception 'Invite code hash is required';
    end if;

    return query
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
        family_invites.family_id;

    if not found then
        raise exception 'Invite is invalid, expired, revoked, or already used';
    end if;
end;
$$;

revoke all on function public.redeem_family_invite(text)
from public;

grant execute on function public.redeem_family_invite(text)
to authenticated;
