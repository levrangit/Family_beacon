-- ============================================================
-- FIX DEVICE COMMAND STALE RECOVERY
-- Return recovered commands correctly from the UPDATE statement.
-- ============================================================

create or replace function public.recover_stale_device_commands(
    target_token_hash text,
    stale_after_seconds integer default 120
)
returns setof public.commands
language plpgsql
security definer
set search_path = public
as $$
declare
    target_device_id uuid;
begin
    -- Authenticate device by token hash.
    select dat.device_id
    into target_device_id
    from public.device_auth_tokens dat
    where dat.token_hash = target_token_hash
      and dat.revoked_at is null
    limit 1;

    if target_device_id is null then
        raise exception 'Invalid device token';
    end if;

    if stale_after_seconds < 1 then
        raise exception 'Invalid stale timeout';
    end if;

    -- Record token usage.
    update public.device_auth_tokens
    set last_used_at = now()
    where token_hash = target_token_hash
      and revoked_at is null;

    -- Re-queue stale commands and return the recovered rows.
    return query
    update public.commands
    set
        status = 'pending',
        sent_at = null,
        executed_at = null,
        result = null,
        error_message = null
    where device_id = target_device_id
      and status = 'executing'::public.command_status
      and sent_at is not null
      and sent_at < now() - make_interval(
          secs => stale_after_seconds
      )
    returning *;
end;
$$;


-- ============================================================
-- FUNCTION PERMISSIONS
-- ============================================================

revoke all
on function public.recover_stale_device_commands(
    text,
    integer
)
from public, anon, authenticated, service_role;

grant execute
on function public.recover_stale_device_commands(
    text,
    integer
)
to anon, authenticated;
