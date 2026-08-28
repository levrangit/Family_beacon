-- ============================================================
-- Family Beacon
-- Migration: 001_initial
-- Database: Supabase PostgreSQL
--
-- SQLite is NOT used.
-- ============================================================

create extension if not exists pgcrypto;


-- ============================================================
-- ENUM TYPES
-- ============================================================

create type public.member_type as enum (
    'parent',
    'child'
);

create type public.device_platform as enum (
    'windows',
    'macos',
    'linux'
);

create type public.command_status as enum (
    'pending',
    'sent',
    'executing',
    'completed',
    'failed',
    'cancelled'
);

create type public.command_type as enum (
    'lock',
    'unlock',
    'add_time',
    'remove_time',
    'get_status'
);


-- ============================================================
-- PROFILES
-- Links application user to Supabase Auth user.
-- ============================================================

create table public.profiles (
    id uuid primary key
        references auth.users(id)
        on delete cascade,

    display_name text,

    telegram_id bigint unique,

    role text not null default 'parent'
        check (role in ('parent', 'admin')),

    is_active boolean not null default true,

    created_at timestamptz not null default now(),

    updated_at timestamptz not null default now()
);


-- ============================================================
-- FAMILIES
-- ============================================================

create table public.families (
    id uuid primary key default gen_random_uuid(),

    name text not null,

    created_at timestamptz not null default now(),

    updated_at timestamptz not null default now()
);


-- ============================================================
-- FAMILY MEMBERS
-- ============================================================

create table public.family_members (
    id uuid primary key default gen_random_uuid(),

    family_id uuid not null
        references public.families(id)
        on delete cascade,

    profile_id uuid not null
        references public.profiles(id)
        on delete cascade,

    member_type public.member_type not null,

    created_at timestamptz not null default now(),

    unique (family_id, profile_id)
);


-- ============================================================
-- CHILDREN
-- ============================================================

create table public.children (
    id uuid primary key default gen_random_uuid(),

    family_id uuid not null
        references public.families(id)
        on delete cascade,

    name text not null,

    avatar_url text,

    is_active boolean not null default true,

    created_at timestamptz not null default now(),

    updated_at timestamptz not null default now()
);


-- ============================================================
-- DEVICES
-- ============================================================

create table public.devices (
    id uuid primary key default gen_random_uuid(),

    child_id uuid not null
        references public.children(id)
        on delete cascade,

    device_id text not null unique,

    name text not null,

    platform public.device_platform not null,

    hostname text,

    agent_version text,

    is_online boolean not null default false,

    last_seen timestamptz,

    created_at timestamptz not null default now(),

    updated_at timestamptz not null default now()
);


-- ============================================================
-- TIME POLICIES
-- ============================================================

create table public.time_policies (
    id uuid primary key default gen_random_uuid(),

    child_id uuid not null
        references public.children(id)
        on delete cascade,

    day_of_week smallint not null
        check (day_of_week between 0 and 6),

    daily_limit_minutes integer not null
        check (daily_limit_minutes >= 0),

    start_time time,

    end_time time,

    is_enabled boolean not null default true,

    created_at timestamptz not null default now(),

    updated_at timestamptz not null default now(),

    unique (child_id, day_of_week)
);


-- ============================================================
-- TIME USAGE
-- ============================================================

create table public.time_usage (
    id uuid primary key default gen_random_uuid(),

    child_id uuid not null
        references public.children(id)
        on delete cascade,

    device_id uuid not null
        references public.devices(id)
        on delete cascade,

    usage_date date not null,

    used_minutes integer not null default 0
        check (used_minutes >= 0),

    created_at timestamptz not null default now(),

    updated_at timestamptz not null default now(),

    unique (child_id, device_id, usage_date)
);


-- ============================================================
-- COMMANDS
-- Commands waiting for / sent to child agent.
-- ============================================================

create table public.commands (
    id uuid primary key default gen_random_uuid(),

    device_id uuid not null
        references public.devices(id)
        on delete cascade,

    command public.command_type not null,

    payload jsonb not null default '{}'::jsonb,

    status public.command_status not null default 'pending',

    result jsonb,

    error_message text,

    created_by uuid
        references public.profiles(id)
        on delete set null,

    created_at timestamptz not null default now(),

    sent_at timestamptz,

    executed_at timestamptz,

    updated_at timestamptz not null default now()
);


-- ============================================================
-- AUDIT LOG
-- Family-level audit trail.
-- ============================================================

create table public.audit_log (
    id uuid primary key default gen_random_uuid(),

    family_id uuid not null
        references public.families(id)
        on delete cascade,

    actor_id uuid
        references public.profiles(id)
        on delete set null,

    action text not null,

    target_type text,

    target_id uuid,

    metadata jsonb not null default '{}'::jsonb,

    created_at timestamptz not null default now()
);


-- ============================================================
-- INDEXES
-- ============================================================

create index idx_profiles_telegram_id
    on public.profiles(telegram_id);

create index idx_family_members_family_id
    on public.family_members(family_id);

create index idx_family_members_profile_id
    on public.family_members(profile_id);

create index idx_children_family_id
    on public.children(family_id);

create index idx_devices_child_id
    on public.devices(child_id);

create index idx_devices_last_seen
    on public.devices(last_seen);

create index idx_time_policies_child_id
    on public.time_policies(child_id);

create index idx_time_usage_child_date
    on public.time_usage(child_id, usage_date);

create index idx_time_usage_device_date
    on public.time_usage(device_id, usage_date);

create index idx_commands_device_status
    on public.commands(device_id, status);

create index idx_commands_created_at
    on public.commands(created_at desc);

create index idx_audit_log_family_created
    on public.audit_log(family_id, created_at desc);

create index idx_audit_log_actor_id
    on public.audit_log(actor_id);


-- ============================================================
-- UPDATED_AT FUNCTION
-- ============================================================

create or replace function public.set_updated_at()
returns trigger
language plpgsql
security invoker
set search_path = public
as $$
begin
    new.updated_at = now();
    return new;
end;
$$;


-- ============================================================
-- UPDATED_AT TRIGGERS
-- ============================================================

create trigger profiles_set_updated_at
before update on public.profiles
for each row
execute function public.set_updated_at();

create trigger families_set_updated_at
before update on public.families
for each row
execute function public.set_updated_at();

create trigger children_set_updated_at
before update on public.children
for each row
execute function public.set_updated_at();

create trigger devices_set_updated_at
before update on public.devices
for each row
execute function public.set_updated_at();

create trigger time_policies_set_updated_at
before update on public.time_policies
for each row
execute function public.set_updated_at();

create trigger time_usage_set_updated_at
before update on public.time_usage
for each row
execute function public.set_updated_at();

create trigger commands_set_updated_at
before update on public.commands
for each row
execute function public.set_updated_at();


-- ============================================================
-- RLS HELPER FUNCTIONS
-- ============================================================

create or replace function public.is_family_member(
    target_family_id uuid
)
returns boolean
language sql
security definer
stable
set search_path = public
as $$
    select exists (
        select 1
        from public.family_members fm
        where fm.family_id = target_family_id
          and fm.profile_id = auth.uid()
    );
$$;


create or replace function public.is_family_parent(
    target_family_id uuid
)
returns boolean
language sql
security definer
stable
set search_path = public
as $$
    select exists (
        select 1
        from public.family_members fm
        where fm.family_id = target_family_id
          and fm.profile_id = auth.uid()
          and fm.member_type = 'parent'
    );
$$;


create or replace function public.child_family_id(
    target_child_id uuid
)
returns uuid
language sql
security definer
stable
set search_path = public
as $$
    select c.family_id
    from public.children c
    where c.id = target_child_id;
$$;


create or replace function public.device_family_id(
    target_device_id uuid
)
returns uuid
language sql
security definer
stable
set search_path = public
as $$
    select c.family_id
    from public.devices d
    join public.children c
        on c.id = d.child_id
    where d.id = target_device_id;
$$;


-- ============================================================
-- PROFILE CREATION AFTER SUPABASE AUTH REGISTRATION
-- ============================================================

create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
    insert into public.profiles (
        id,
        display_name
    )
    values (
        new.id,
        coalesce(
            new.raw_user_meta_data ->> 'full_name',
            new.raw_user_meta_data ->> 'name'
        )
    );

    return new;
end;
$$;


create trigger on_auth_user_created
after insert on auth.users
for each row
execute function public.handle_new_user();


-- ============================================================
-- CREATE FAMILY
--
-- Creates:
--   1. family
--   2. current authenticated user as parent
--
-- This operation is atomic.
-- ============================================================

create or replace function public.create_family(
    family_name text
)
returns uuid
language plpgsql
security definer
set search_path = public
as $$
declare
    new_family_id uuid;
    current_user_id uuid;
begin
    current_user_id := auth.uid();

    if current_user_id is null then
        raise exception 'Authentication required';
    end if;

    if not exists (
        select 1
        from public.profiles
        where id = current_user_id
          and is_active = true
    ) then
        raise exception 'Active profile not found';
    end if;

    if family_name is null
       or length(trim(family_name)) = 0 then
        raise exception 'Family name cannot be empty';
    end if;

    insert into public.families (
        name
    )
    values (
        trim(family_name)
    )
    returning id into new_family_id;

    insert into public.family_members (
        family_id,
        profile_id,
        member_type
    )
    values (
        new_family_id,
        current_user_id,
        'parent'
    );

    return new_family_id;
end;
$$;


-- ============================================================
-- TIME USAGE CONSISTENCY CHECK
--
-- Ensures that:
--
-- time_usage.child_id
--     =
-- devices.child_id
--
-- for the referenced device.
-- ============================================================

create or replace function public.validate_time_usage_device()
returns trigger
language plpgsql
security invoker
set search_path = public
as $$
declare
    device_child_id uuid;
begin
    select d.child_id
    into device_child_id
    from public.devices d
    where d.id = new.device_id;

    if device_child_id is null then
        raise exception 'Device does not exist: %', new.device_id;
    end if;

    if device_child_id <> new.child_id then
        raise exception
            'Device % does not belong to child %',
            new.device_id,
            new.child_id;
    end if;

    return new;
end;
$$;


create trigger time_usage_validate_device
before insert or update on public.time_usage
for each row
execute function public.validate_time_usage_device();


-- ============================================================
-- ENABLE RLS
-- ============================================================

alter table public.profiles enable row level security;
alter table public.families enable row level security;
alter table public.family_members enable row level security;
alter table public.children enable row level security;
alter table public.devices enable row level security;
alter table public.time_policies enable row level security;
alter table public.time_usage enable row level security;
alter table public.commands enable row level security;
alter table public.audit_log enable row level security;


-- ============================================================
-- PROFILES POLICIES
-- ============================================================

create policy "Users can view own profile"
on public.profiles
for select
to authenticated
using (
    id = auth.uid()
);


-- Users may only update their display name.
-- Sensitive fields:
--   role
--   is_active
--   telegram_id
-- cannot be changed by the authenticated user.

create policy "Users can update own display name"
on public.profiles
for update
to authenticated
using (
    id = auth.uid()
)
with check (
    id = auth.uid()
    and role = (
        select p.role
        from public.profiles p
        where p.id = auth.uid()
    )
    and is_active = (
        select p.is_active
        from public.profiles p
        where p.id = auth.uid()
    )
    and telegram_id is not distinct from (
        select p.telegram_id
        from public.profiles p
        where p.id = auth.uid()
    )
);


-- ============================================================
-- FAMILIES POLICIES
-- ============================================================

-- Direct INSERT into families is intentionally NOT allowed.
-- Families must be created through public.create_family().

create policy "Family members can view their family"
on public.families
for select
to authenticated
using (
    public.is_family_member(id)
);


create policy "Family parents can update their family"
on public.families
for update
to authenticated
using (
    public.is_family_parent(id)
)
with check (
    public.is_family_parent(id)
);


-- ============================================================
-- FAMILY MEMBERS POLICIES
-- ============================================================

create policy "Family members can view memberships"
on public.family_members
for select
to authenticated
using (
    public.is_family_member(family_id)
);


create policy "Family parents can add members"
on public.family_members
for insert
to authenticated
with check (
    public.is_family_parent(family_id)
);


create policy "Family parents can update members"
on public.family_members
for update
to authenticated
using (
    public.is_family_parent(family_id)
)
with check (
    public.is_family_parent(family_id)
);


create policy "Family parents can remove members"
on public.family_members
for delete
to authenticated
using (
    public.is_family_parent(family_id)
);


-- ============================================================
-- CHILDREN POLICIES
-- ============================================================

create policy "Family members can view children"
on public.children
for select
to authenticated
using (
    public.is_family_member(family_id)
);


create policy "Family parents can create children"
on public.children
for insert
to authenticated
with check (
    public.is_family_parent(family_id)
);


create policy "Family parents can update children"
on public.children
for update
to authenticated
using (
    public.is_family_parent(family_id)
)
with check (
    public.is_family_parent(family_id)
);


create policy "Family parents can delete children"
on public.children
for delete
to authenticated
using (
    public.is_family_parent(family_id)
);


-- ============================================================
-- DEVICES POLICIES
-- ============================================================

create policy "Family members can view devices"
on public.devices
for select
to authenticated
using (
    public.is_family_member(
        public.child_family_id(child_id)
    )
);


create policy "Family parents can create devices"
on public.devices
for insert
to authenticated
with check (
    public.is_family_parent(
        public.child_family_id(child_id)
    )
);


create policy "Family parents can update devices"
on public.devices
for update
to authenticated
using (
    public.is_family_parent(
        public.child_family_id(child_id)
    )
)
with check (
    public.is_family_parent(
        public.child_family_id(child_id)
    )
);


create policy "Family parents can delete devices"
on public.devices
for delete
to authenticated
using (
    public.is_family_parent(
        public.child_family_id(child_id)
    )
);


-- ============================================================
-- TIME POLICIES
-- ============================================================

create policy "Family members can view time policies"
on public.time_policies
for select
to authenticated
using (
    public.is_family_member(
        public.child_family_id(child_id)
    )
);


create policy "Family parents can create time policies"
on public.time_policies
for insert
to authenticated
with check (
    public.is_family_parent(
        public.child_family_id(child_id)
    )
);


create policy "Family parents can update time policies"
on public.time_policies
for update
to authenticated
using (
    public.is_family_parent(
        public.child_family_id(child_id)
    )
)
with check (
    public.is_family_parent(
        public.child_family_id(child_id)
    )
);


create policy "Family parents can delete time policies"
on public.time_policies
for delete
to authenticated
using (
    public.is_family_parent(
        public.child_family_id(child_id)
    )
);


-- ============================================================
-- TIME USAGE
-- ============================================================

create policy "Family members can view time usage"
on public.time_usage
for select
to authenticated
using (
    public.is_family_member(
        public.child_family_id(child_id)
    )
);


-- ============================================================
-- COMMANDS
-- ============================================================

create policy "Family members can view commands"
on public.commands
for select
to authenticated
using (
    public.is_family_member(
        public.device_family_id(device_id)
    )
);


create policy "Family parents can create commands"
on public.commands
for insert
to authenticated
with check (
    public.is_family_parent(
        public.device_family_id(device_id)
    )
    and created_by = auth.uid()
);


-- ============================================================
-- AUDIT LOG
-- ============================================================

create policy "Family members can view audit log"
on public.audit_log
for select
to authenticated
using (
    public.is_family_member(family_id)
);


-- ============================================================
-- GRANTS
-- ============================================================

revoke all on public.profiles
from anon, authenticated;

revoke all on public.families
from anon, authenticated;

revoke all on public.family_members
from anon, authenticated;

revoke all on public.children
from anon, authenticated;

revoke all on public.devices
from anon, authenticated;

revoke all on public.time_policies
from anon, authenticated;

revoke all on public.time_usage
from anon, authenticated;

revoke all on public.commands
from anon, authenticated;

revoke all on public.audit_log
from anon, authenticated;


-- ============================================================
-- TABLE GRANTS
-- ============================================================

grant select, update
on public.profiles
to authenticated;


grant select, update
on public.families
to authenticated;


grant select, insert, update, delete
on public.family_members
to authenticated;


grant select, insert, update, delete
on public.children
to authenticated;


grant select, insert, update, delete
on public.devices
to authenticated;


grant select, insert, update, delete
on public.time_policies
to authenticated;


grant select
on public.time_usage
to authenticated;


grant select, insert
on public.commands
to authenticated;


grant select
on public.audit_log
to authenticated;


-- ============================================================
-- FUNCTION PERMISSIONS
-- ============================================================

-- ------------------------------------------------------------
-- RLS helper functions
--
-- These functions are used by RLS policies.
-- Authenticated users need EXECUTE access.
-- Anonymous users must not have access.
-- ------------------------------------------------------------

revoke all
on function public.is_family_member(uuid)
from public, anon, authenticated, service_role;

grant execute
on function public.is_family_member(uuid)
to authenticated;


revoke all
on function public.is_family_parent(uuid)
from public, anon, authenticated, service_role;

grant execute
on function public.is_family_parent(uuid)
to authenticated;


revoke all
on function public.child_family_id(uuid)
from public, anon, authenticated, service_role;

grant execute
on function public.child_family_id(uuid)
to authenticated;


revoke all
on function public.device_family_id(uuid)
from public, anon, authenticated, service_role;

grant execute
on function public.device_family_id(uuid)
to authenticated;


-- ------------------------------------------------------------
-- create_family
--
-- Creates a family and makes the current authenticated user
-- the first parent.
--
-- Anonymous users must NOT be able to execute this function.
-- Authenticated users can execute it.
-- service_role is allowed for trusted backend operations.
-- ------------------------------------------------------------

revoke all
on function public.create_family(text)
from public, anon, authenticated, service_role;

grant execute
on function public.create_family(text)
to authenticated, service_role;


-- ------------------------------------------------------------
-- handle_new_user
--
-- This function is executed by the trigger on auth.users.
-- It must not be callable by normal clients.
-- ------------------------------------------------------------

revoke all
on function public.handle_new_user()
from public, anon, authenticated, service_role;


-- ------------------------------------------------------------
-- validate_time_usage_device
--
-- This function is executed by a database trigger.
-- It must not be callable by normal clients.
-- ------------------------------------------------------------

revoke all
on function public.validate_time_usage_device()
from public, anon, authenticated, service_role;


-- ============================================================
-- END OF MIGRATION
-- ============================================================