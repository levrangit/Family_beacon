-- ============================================================
-- DEVICE AUTH TOKEN RPC
-- Stores a device token hash only after verifying that the
-- authenticated user is a parent of the device's family.
-- ============================================================

create or replace function public.create_device_auth_token(
    target_device_id uuid,
    target_token_hash text
)
returns public.device_auth_tokens
language plpgsql
security definer
set search_path = public
as $$
declare
    target_family_id uuid;
    result_row public.device_auth_tokens;
begin
    -- Find the family that owns the device.
    target_family_id := public.device_family_id(target_device_id);

    if target_family_id is null then
        raise exception 'Device not found';
    end if;

    -- Only a family parent may issue a device token.
    if not public.is_family_parent(target_family_id) then
        raise exception 'Permission denied';
    end if;

    -- Revoke all previously active tokens for this device.
    update public.device_auth_tokens
    set revoked_at = now()
    where device_id = target_device_id
      and revoked_at is null;

    -- Store only the hash of the new token.
    insert into public.device_auth_tokens (
        device_id,
        token_hash
    )
    values (
        target_device_id,
        target_token_hash
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
on function public.create_device_auth_token(uuid, text)
from public, anon, authenticated, service_role;

grant execute
on function public.create_device_auth_token(uuid, text)
to authenticated;
