-- ============================================================
-- CREATE COMMAND RPC
-- Creates a command for a device on behalf of the
-- currently authenticated family parent.
-- ============================================================

create or replace function public.create_command(
    target_device_id uuid,
    target_command public.command_type,
    target_payload jsonb default '{}'::jsonb
)
returns public.commands
language plpgsql
security definer
set search_path = public
as $$
declare
    target_family_id uuid;
    result_row public.commands;
begin
    target_family_id := public.device_family_id(target_device_id);

    if target_family_id is null then
        raise exception 'Device not found';
    end if;

    if not public.is_family_parent(target_family_id) then
        raise exception 'Permission denied';
    end if;

    insert into public.commands (
        device_id,
        command,
        payload,
        created_by
    )
    values (
        target_device_id,
        target_command,
        target_payload,
        auth.uid()
    )
    returning *
    into result_row;

    return result_row;
end;
$$;


-- ============================================================
-- FUNCTION PERMISSIONS
-- ============================================================

revoke all
on function public.create_command(uuid, public.command_type, jsonb)
from public, anon, authenticated, service_role;

grant execute
on function public.create_command(uuid, public.command_type, jsonb)
to authenticated;
