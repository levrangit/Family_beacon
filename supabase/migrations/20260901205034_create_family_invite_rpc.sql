create or replace function public.create_family_invite(
    p_family_id uuid,
    p_code_hash text,
    p_expires_at timestamptz
)
returns table (
    id uuid,
    family_id uuid,
    expires_at timestamptz
)
language plpgsql
security definer
set search_path = public
as $$
begin
    if auth.uid() is null then
        raise exception 'Authentication required';
    end if;

    if not public.is_family_parent(p_family_id) then
        raise exception 'Only a family parent can create an invite';
    end if;

    if nullif(trim(p_code_hash), '') is null then
        raise exception 'Invite code hash is required';
    end if;

    if p_expires_at <= now() then
        raise exception 'Invite expiration must be in the future';
    end if;

    return query
    insert into public.family_invites (
        family_id,
        created_by,
        code_hash,
        expires_at
    )
    values (
        p_family_id,
        auth.uid(),
        p_code_hash,
        p_expires_at
    )
    returning
        family_invites.id,
        family_invites.family_id,
        family_invites.expires_at;
end;
$$;

revoke all on function public.create_family_invite(uuid, text, timestamptz)
from public;

grant execute on function public.create_family_invite(uuid, text, timestamptz)
to authenticated;

create policy "Family parents can view family invites"
on public.family_invites
for select
to authenticated
using (
    public.is_family_parent(family_id)
);

create policy "Family parents can revoke family invites"
on public.family_invites
for update
to authenticated
using (
    public.is_family_parent(family_id)
)
with check (
    public.is_family_parent(family_id)
);
