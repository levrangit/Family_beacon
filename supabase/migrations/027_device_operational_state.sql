-- ============================================================
-- Family Beacon
-- Migration: 027_device_operational_state
-- Database: Supabase PostgreSQL
--
-- Add the operational state required by the Device Update
-- architecture and introduce a heartbeat RPC that accepts the
-- Agent's reported installed version.
--
-- This migration is committed to Git only. It must be applied to
-- local Supabase and verified there before any remote application.
-- ============================================================

DO $$
BEGIN
    CREATE TYPE public.device_update_status AS ENUM (
        'idle',
        'available',
        'requested',
        'downloading',
        'verifying',
        'installing',
        'restarting',
        'health_check',
        'success',
        'download_failed',
        'verify_failed',
        'install_failed',
        'health_check_failed',
        'rolling_back',
        'rolled_back'
    );
EXCEPTION
    WHEN duplicate_object THEN NULL;
END
$$;

ALTER TABLE public.devices
    ADD COLUMN IF NOT EXISTS target_agent_version text;

ALTER TABLE public.devices
    ADD COLUMN IF NOT EXISTS update_status public.device_update_status;

UPDATE public.devices
SET update_status = 'idle'
WHERE update_status IS NULL;

ALTER TABLE public.devices
    ALTER COLUMN update_status SET DEFAULT 'idle';

ALTER TABLE public.devices
    ALTER COLUMN update_status SET NOT NULL;

CREATE INDEX IF NOT EXISTS devices_update_status_idx
    ON public.devices(update_status);

-- ============================================================
-- DEVICE AGENT HEARTBEAT V2
-- ============================================================

CREATE OR REPLACE FUNCTION public.device_heartbeat_by_token_v2(
    target_token_hash text,
    reported_agent_version text
)
RETURNS public.devices
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    target_device_id uuid;
    result_row public.devices;
BEGIN
    IF nullif(trim(target_token_hash), '') IS NULL THEN
        RAISE EXCEPTION 'Device token is required';
    END IF;

    IF nullif(trim(reported_agent_version), '') IS NULL THEN
        RAISE EXCEPTION 'Agent version is required';
    END IF;

    SELECT dat.device_id
    INTO target_device_id
    FROM public.device_auth_tokens dat
    WHERE dat.token_hash = target_token_hash
      AND dat.revoked_at IS NULL
    LIMIT 1;

    IF target_device_id IS NULL THEN
        RAISE EXCEPTION 'Invalid device token';
    END IF;

    UPDATE public.devices
    SET
        agent_version = trim(reported_agent_version),
        is_online = true,
        last_seen = now(),
        updated_at = now()
    WHERE id = target_device_id
    RETURNING *
    INTO result_row;

    IF result_row.id IS NULL THEN
        RAISE EXCEPTION 'Device not found';
    END IF;

    UPDATE public.device_auth_tokens
    SET last_used_at = now()
    WHERE token_hash = target_token_hash
      AND revoked_at IS NULL;

    RETURN result_row;
END;
$$;

REVOKE ALL
ON FUNCTION public.device_heartbeat_by_token_v2(text, text)
FROM public, anon, authenticated, service_role;

grant execute
ON FUNCTION public.device_heartbeat_by_token_v2(text, text)
TO anon, authenticated;
