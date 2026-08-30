-- ============================================================
-- DEVICE AGENT HEARTBEAT
-- Updates device online state using the device auth token.
-- The device is identified by the token, not by request data.
-- ============================================================

create or replace function public.device_heartbeat_by_token(
    target_token_hash text
)
returns public.devices
language plpgsql
security definer
set search_path = public
as $$
declare
    target_device_id uuid;
    result_row public.devices;
begin
    -- Authenticate device using the stored token hash.
    select dat.device_id
    into target_device_id
    from public.device_auth_tokens dat
    where dat.token_hash = target_token_hash
      and dat.revoked_at is null
    limit 1;

    if target_device_id is null then
        raise exception 'Invalid device token';
    end if;

    -- Mark the device as online.
    update public.devices
    set
        is_online = true,
        last_seen = now(),
        updated_at = now()
    where id = target_device_id
    returning *
    into result_row;

    if result_row.id is null then
        raise exception 'Device not found';
    end if;

    -- Record token usage.
    update public.device_auth_tokens
    set last_used_at = now()
    where token_hash = target_token_hash
      and revoked_at is null;

    return result_row;
end;
$$;


-- ============================================================
-- FUNCTION PERMISSIONS
-- ============================================================

revoke all
on function public.device_heartbeat_by_token(text)
from public, anon, authenticated, service_role;

grant execute
on function public.device_heartbeat_by_token(text)
to anon, authenticated;
