-- ============================================================
-- DEVICE HEARTBEAT
-- ============================================================

create or replace function public.device_heartbeat(
    device_uuid uuid
)
returns public.devices
language plpgsql
security definer
set search_path = public
as $$
declare
    updated_device public.devices;
begin
    update public.devices d
    set
        is_online = true,
        last_seen = now(),
        updated_at = now()
    where d.id = device_uuid
      and exists (
          select 1
          from public.children c
          where c.id = d.child_id
            and public.is_family_member(c.family_id)
      )
    returning d.* into updated_device;

    if updated_device.id is null then
        raise exception 'Device not found';
    end if;

    return updated_device;
end;
$$;

revoke all on function public.device_heartbeat(uuid)
from public;

grant execute on function public.device_heartbeat(uuid)
to authenticated;
