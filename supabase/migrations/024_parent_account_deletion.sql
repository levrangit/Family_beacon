-- ============================================================
-- Family Beacon
-- Migration: 024_parent_account_deletion
-- Database: Supabase PostgreSQL
--
-- Parent self-deletion support:
-- - identifies the family/families owned by the parent profile
-- - deletes those families and their cascaded family data
-- - deletes the parent profile
-- - leaves other parent profiles in the deleted family untouched
-- - Auth user deletion is performed by the backend Admin API
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
    profile_exists boolean;
begin
    if p_profile_id is null then
        raise exception 'Profile ID is required';
    end if;

    select exists (
        select 1
        from public.profiles
        where id = p_profile_id
          and role = 'parent'
    )
    into profile_exists;

    if not profile_exists then
        raise exception 'Parent profile not found';
    end if;

    for family_record in
        select distinct family_id
        from public.family_members
        where profile_id = p_profile_id
          and member_type = 'parent'
    loop
        delete from public.families
        where id = family_record.family_id;
    end loop;

    delete from public.profiles
    where id = p_profile_id;
end;
$$;

revoke all on function public.delete_parent_account(uuid)
from public;

grant execute on function public.delete_parent_account(uuid)
to service_role;
