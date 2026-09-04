-- ============================================================
-- Family Beacon
-- Migration: 024_parent_account_deletion
-- Database: Supabase PostgreSQL
--
-- Parent self-deletion support:
-- - removes the parent from every family
-- - deletes a family only when the parent is its only parent
-- - preserves families that have another parent
-- - cascades family data only when the family itself is deleted
-- - removes invites created by the deleted parent
-- - clears used_by references to the deleted parent
-- - deletes the parent profile
-- - Auth user deletion is performed separately by the backend
-- ============================================================

create or replace function public.delete_parent_account(
    p_profile_id uuid
)
returns void
language plpgsql
security definer
set search_path = public
as $$
declare
    family_record record;
    parent_count integer;
begin
    if p_profile_id is null then
        raise exception 'Profile ID is required';
    end if;

    if not exists (
        select 1
        from public.profiles
        where id = p_profile_id
          and role = 'parent'
    ) then
        raise exception 'Parent profile not found';
    end if;

    -- Process every family in which this parent is a member.
    for family_record in
        select distinct family_id
        from public.family_members
        where profile_id = p_profile_id
          and member_type = 'parent'
    loop
        select count(*)
        into parent_count
        from public.family_members
        where family_id = family_record.family_id
          and member_type = 'parent';

        if parent_count <= 1 then
            -- The deleting parent is the only parent.
            -- Deleting the family cascades its family data.
            delete from public.families
            where id = family_record.family_id;
        else
            -- Another parent remains, so preserve the family
            -- and remove only the deleting parent's membership.
            delete from public.family_members
            where family_id = family_record.family_id
              and profile_id = p_profile_id
              and member_type = 'parent';
        end if;
    end loop;

    -- Invites created by this parent cannot keep a foreign-key
    -- reference to a profile that is about to be deleted.
    delete from public.family_invites
    where created_by = p_profile_id;

    -- The parent may also have been recorded as the user who
    -- redeemed another parent's invite. That reference is nullable.
    update public.family_invites
    set used_by = null
    where used_by = p_profile_id;

    -- family_members.profile_id has ON DELETE CASCADE, so any
    -- remaining membership rows are removed automatically.
    delete from public.profiles
    where id = p_profile_id;
end;
$$;

revoke all on function public.delete_parent_account(uuid)
from public;

grant execute on function public.delete_parent_account(uuid)
to service_role;
