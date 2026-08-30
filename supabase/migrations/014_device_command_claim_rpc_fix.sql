-- ============================================================
-- DEVICE COMMAND CLAIM RPC FIX
-- Return zero rows when there is no pending command.
-- ============================================================

drop function if exists public.claim_next_device_command(text);

create function public.claim_next_device_command(
    target_token_hash text
)
returns setof public.commands
language plpgsql
security definer
set search_path = public
as $$
declare
    target_device_id uuid;
    result_row public.commands;
begin
    -- Authenticate the device using the stored token hash.
    select dat.device_id
    into target_device_id
    from public.device_auth_tokens dat
    where dat.token_hash = target_token_hash
      and dat.revoked_at is null
    limit 1;

    if target_device_id is null then
        raise exception 'Invalid device token';
    end if;

    -- Record token usage.
    update public.device_auth_tokens
    set last_used_at = now()
    where token_hash = target_token_hash
      and revoked_at is null;

    -- Atomically claim one pending command for this device.
    update public.commands
    set
        status = 'executing',
        sent_at = coalesce(sent_at, now())
    where id = (
        select c.id
        from public.commands c
        where c.device_id = target_device_id
          and c.status = 'pending'
        order by c.created_at
        for update skip locked
        limit 1
    )
    returning *
    into result_row;

    -- Return one row only when a command was actually claimed.
    if result_row.id is not null then
        return next result_row;
    end if;

    -- No pending command: return zero rows.
    return;
end;
$$;

-- ============================================================
-- FUNCTION PERMISSIONS
-- ============================================================

revoke all
on function public.claim_next_device_command(text)
from public, anon, authenticated, service_role;

grant execute
on function public.claim_next_device_command(text)
to anon, authenticated;
