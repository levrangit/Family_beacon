-- ============================================================
-- Family Beacon
-- Migration: 032_agent_installations
-- Database: Supabase PostgreSQL
--
-- Bootstrap installations for the Device Agent.
-- A parent creates a short-lived installation code in Telegram.
-- The official installer uses that code once and supplies a unique
-- secret for that Agent instance. The secret is stored only as a hash.
--
-- This migration is committed to Git only. Do not apply it to the
-- remote Supabase project as part of this change.
-- ============================================================

CREATE TABLE IF NOT EXISTS public.agent_installations (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),

    family_id uuid NOT NULL
        REFERENCES public.families(id)
        ON DELETE CASCADE,

    installation_code_hash text NOT NULL UNIQUE,

    agent_secret_hash text,

    status text NOT NULL DEFAULT 'pending',

    device_platform public.device_platform,
    device_id text,
    hostname text,
    agent_version text,

    expires_at timestamptz NOT NULL,
    claimed_at timestamptz,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),

    CONSTRAINT agent_installations_status_check
        CHECK (status IN ('pending', 'claimed', 'expired', 'cancelled')),

    CONSTRAINT agent_installations_expires_after_create
        CHECK (expires_at > created_at),

    CONSTRAINT agent_installations_claimed_consistency
        CHECK (
            (status <> 'claimed')
            OR (
                agent_secret_hash IS NOT NULL
                AND device_platform IS NOT NULL
                AND device_id IS NOT NULL
                AND claimed_at IS NOT NULL
            )
        )
);

CREATE INDEX IF NOT EXISTS agent_installations_family_status_idx
    ON public.agent_installations(family_id, status);

CREATE INDEX IF NOT EXISTS agent_installations_status_expires_idx
    ON public.agent_installations(status, expires_at);

DROP TRIGGER IF EXISTS agent_installations_set_updated_at
    ON public.agent_installations;

CREATE TRIGGER agent_installations_set_updated_at
BEFORE UPDATE ON public.agent_installations
FOR EACH ROW
EXECUTE FUNCTION public.set_updated_at();

ALTER TABLE public.agent_installations
    ENABLE ROW LEVEL SECURITY;

REVOKE ALL ON public.agent_installations
FROM anon, authenticated;

-- Direct client access is intentionally not granted.
-- Telegram parent and Agent bootstrap operations use trusted Backend code.
