-- ============================================================
-- TIME USAGE RPC
-- Atomically records additional device usage for a child.
-- ============================================================

create or replace function public.record_time_usage(
    target_child_id uuid,
    target_device_id uuid,
    target_usage_date date,
    additional_minutes integer
)
returns public.time_usage
language plpgsql
security definer
set search_path = public
as $$
declare
    device_child_id uuid;
    result_row public.time_usage;
begin
    if additional_minutes < 0 then
        raise exception 'Usage minutes cannot be negative';
    end if;

    select d.child_id
    into device_child_id
    from public.devices d
    where d.id = target_device_id;

    if device_child_id is null then
        raise exception 'Device not found';
    end if;

    if device_child_id <> target_child_id then
        raise exception
            'Device % does not belong to child %',
            target_device_id,
            target_child_id;
    end if;

    if not public.is_family_member(
        public.child_family_id(target_child_id)
    ) then
        raise exception 'Permission denied';
    end if;

    insert into public.time_usage (
        child_id,
        device_id,
        usage_date,
        used_minutes
    )
    values (
        target_child_id,
        target_device_id,
        target_usage_date,
        additional_minutes
    )
    on conflict (child_id, device_id, usage_date)
    do update
    set used_minutes =
        public.time_usage.used_minutes + excluded.used_minutes
    returning *
    into result_row;

    return result_row;
end;
$$;


-- ============================================================
-- FUNCTION PERMISSIONS
-- ============================================================

revoke all
on function public.record_time_usage(uuid, uuid, date, integer)
from public, anon, authenticated, service_role;

grant execute
on function public.record_time_usage(uuid, uuid, date, integer)
to authenticated;
