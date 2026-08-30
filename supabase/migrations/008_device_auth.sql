-- ============================================================
-- DEVICE AUTHENTICATION
-- Dedicated authentication tokens for device agents.
-- ============================================================

create table public.device_auth_tokens (
    id uuid primary key default gen_random_uuid(),

    device_id uuid not null
        references public.devices(id)
        on delete cascade,

    token_hash text not null unique,

    created_at timestamptz not null default now(),

    last_used_at timestamptz,

    revoked_at timestamptz
);


-- ============================================================
-- INDEXES
-- ============================================================

create index idx_device_auth_tokens_device
    on public.device_auth_tokens(device_id);

create index idx_device_auth_tokens_active
    on public.device_auth_tokens(device_id)
    where revoked_at is null;


-- ============================================================
-- ROW LEVEL SECURITY
-- ============================================================

alter table public.device_auth_tokens enable row level security;


-- ============================================================
-- DEVICE TOKEN LOOKUP
-- ============================================================

create or replace function public.authenticate_device(
    target_token_hash text
)
returns uuid
language sql
security definer
stable
set search_path = public
as $$
    select dat.device_id
    from public.device_auth_tokens dat
    join public.devices d
        on d.id = dat.device_id
    where dat.token_hash = target_token_hash
      and dat.revoked_at is null
    limit 1;
$$;


-- ============================================================
-- FUNCTION PERMISSIONS
-- ============================================================

revoke all
on function public.authenticate_device(text)
from public, anon, authenticated, service_role;

grant execute
on function public.authenticate_device(text)
to anon, authenticated;
