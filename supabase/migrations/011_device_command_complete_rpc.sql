-- ============================================================
-- DEVICE COMMAND COMPLETE RPC
-- Completes a command only when the command belongs to the
-- device authenticated by the supplied device token.
-- ============================================================

drop function if exists public.complete_device_command(
    text,
    uuid,
    text,
    jsonb,
    text
);


create or replace function public.complete_device_command(
    target_token_hash text,
    target_command_id uuid,
    target_status public.command_status,
    target_result jsonb default null,
    target_error_message text default null
)
returns public.commands
language plpgsql
security definer
set search_path = public
as $$
declare
    target_device_id uuid;
    result_row public.commands;
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

    -- Only final command states are allowed.
    if target_status not in ('completed'::public.command_status, 'failed'::public.command_status) then
        raise exception 'Invalid command status';
    end if;

    -- Update only a command belonging to this device.
    update public.commands
    set
        status = target_status,
        result = target_result,
        error_message = target_error_message,
        executed_at = now()
    where id = target_command_id
      and device_id = target_device_id
      and status = 'executing'::public.command_status
    returning *
    into result_row;

    if result_row.id is null then
        raise exception 'Command not found or not executable';
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
on function public.complete_device_command(
    text,
    uuid,
    public.command_status,
    jsonb,
    text
)
from public, anon, authenticated, service_role;

grant execute
on function public.complete_device_command(
    text,
    uuid,
    public.command_status,
    jsonb,
    text
)
to anon, authenticated;
