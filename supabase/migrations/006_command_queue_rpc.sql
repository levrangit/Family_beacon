-- ============================================================
-- COMMAND QUEUE RPC
-- Atomically claims the next pending command for a device.
-- ============================================================

create or replace function public.claim_next_command(
    target_device_id uuid
)
returns public.commands
language plpgsql
security definer
set search_path = public
as $$
declare
    result_row public.commands;
begin
    -- Device must exist.
    if not exists (
        select 1
        from public.devices
        where id = target_device_id
    ) then
        raise exception 'Device not found';
    end if;

    -- Atomically claim one pending command.
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

    return result_row;
end;
$$;


-- ============================================================
-- FUNCTION PERMISSIONS
-- ============================================================

revoke all
on function public.claim_next_command(uuid)
from public, anon, authenticated, service_role;

grant execute
on function public.claim_next_command(uuid)
to authenticated;
