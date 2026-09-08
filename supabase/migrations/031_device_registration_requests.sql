-- ============================================================
-- Family Beacon
-- Migration: 031_device_registration_requests
-- Database: Supabase PostgreSQL
--
-- Central workflow state for Telegram Child -> Parent approval
-- -> Windows Device registration.
--
-- This migration is committed to Git only. Do not apply it to the
-- remote Supabase project as part of this change.
-- ============================================================

DO $$
BEGIN
    CREATE TYPE public.device_registration_status AS ENUM (
        'pending',
        'approved',
        'rejected',
        'cancelled',
        'expired',
        'completed'
    );
EXCEPTION
    WHEN duplicate_object THEN NULL;
END
$$;

CREATE TABLE IF NOT EXISTS public.device_registration_requests (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),

    child_id uuid NOT NULL
        REFERENCES public.children(id)
        ON DELETE CASCADE,

    request_code_hash text NOT NULL UNIQUE,

    status public.device_registration_status NOT NULL
        DEFAULT 'pending',

    device_platform public.device_platform NOT NULL,
    device_id text NOT NULL,
    hostname text,
    agent_version text,

    approved_by_parent_id uuid
        REFERENCES public.profiles(id)
        ON DELETE SET NULL,

    approved_at timestamptz,
    rejected_at timestamptz,
    cancelled_at timestamptz,
    completed_at timestamptz,

    expires_at timestamptz NOT NULL,

    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),

    CONSTRAINT device_registration_requests_expires_after_create
        CHECK (expires_at > created_at),

    CONSTRAINT device_registration_requests_approved_consistency
        CHECK (
            (status <> 'approved')
            OR (approved_by_parent_id IS NOT NULL AND approved_at IS NOT NULL)
        ),

    CONSTRAINT device_registration_requests_rejected_consistency
        CHECK (
            (status <> 'rejected')
            OR rejected_at IS NOT NULL
        ),

    CONSTRAINT device_registration_requests_cancelled_consistency
        CHECK (
            (status <> 'cancelled')
            OR cancelled_at IS NOT NULL
        ),

    CONSTRAINT device_registration_requests_completed_consistency
        CHECK (
            (status <> 'completed')
            OR completed_at IS NOT NULL
        )
);

CREATE INDEX IF NOT EXISTS device_registration_requests_child_status_idx
    ON public.device_registration_requests(child_id, status);

CREATE INDEX IF NOT EXISTS device_registration_requests_status_expires_idx
    ON public.device_registration_requests(status, expires_at);

CREATE INDEX IF NOT EXISTS device_registration_requests_device_id_idx
    ON public.device_registration_requests(device_id);

DROP TRIGGER IF EXISTS device_registration_requests_set_updated_at
    ON public.device_registration_requests;

CREATE TRIGGER device_registration_requests_set_updated_at
BEFORE UPDATE ON public.device_registration_requests
FOR EACH ROW
EXECUTE FUNCTION public.set_updated_at();

ALTER TABLE public.device_registration_requests
    ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Family parents can view device registration requests"
ON public.device_registration_requests
FOR SELECT
TO authenticated
USING (
    public.is_family_parent(public.child_family_id(child_id))
);

CREATE POLICY "Family parents can update device registration requests"
ON public.device_registration_requests
FOR UPDATE
TO authenticated
USING (
    public.is_family_parent(public.child_family_id(child_id))
)
WITH CHECK (
    public.is_family_parent(public.child_family_id(child_id))
);

REVOKE ALL ON public.device_registration_requests
FROM anon, authenticated;

GRANT SELECT, UPDATE
ON public.device_registration_requests
TO authenticated;

-- Direct INSERT is intentionally not granted to normal clients.
-- Backend workflow code will create requests through trusted server-side
-- operations and enforce state transitions:
--
-- pending -> approved | rejected | cancelled | expired
-- approved -> completed | cancelled | expired
--
-- Terminal states:
-- rejected, cancelled, expired, completed
