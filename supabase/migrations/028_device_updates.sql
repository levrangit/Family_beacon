-- ============================================================
-- Family Beacon
-- Migration: 028_device_updates
-- Database: Supabase PostgreSQL
--
-- PR2: persist device update attempts and protect the history
-- with family-scoped RLS. Update lifecycle execution remains an
-- application/Device Agent responsibility; release and
-- compatibility models belong to PR3.
-- ============================================================

CREATE TABLE public.device_updates (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),

    device_id uuid NOT NULL
        REFERENCES public.devices(id)
        ON DELETE CASCADE,

    component text NOT NULL
        CHECK (length(trim(component)) > 0),

    from_version text,

    target_version text NOT NULL
        CHECK (length(trim(target_version)) > 0),

    status public.device_update_status NOT NULL DEFAULT 'requested',

    attempt integer NOT NULL DEFAULT 1
        CHECK (attempt > 0),

    started_at timestamptz,

    completed_at timestamptz,

    error_code text,

    error_message text,

    rollback_version text,

    created_at timestamptz NOT NULL DEFAULT now(),

    updated_at timestamptz NOT NULL DEFAULT now(),

    CONSTRAINT device_updates_completed_after_started
        CHECK (
            completed_at IS NULL
            OR started_at IS NULL
            OR completed_at >= started_at
        )
);

CREATE INDEX device_updates_device_created_idx
    ON public.device_updates(device_id, created_at DESC);

CREATE INDEX device_updates_device_status_idx
    ON public.device_updates(device_id, status);

CREATE INDEX device_updates_status_idx
    ON public.device_updates(status);

CREATE TRIGGER device_updates_set_updated_at
BEFORE UPDATE ON public.device_updates
FOR EACH ROW
EXECUTE FUNCTION public.set_updated_at();

ALTER TABLE public.device_updates ENABLE ROW LEVEL SECURITY;

-- Parents can read update history only for devices belonging to
-- a child in one of their families. There are intentionally no
-- authenticated INSERT/UPDATE/DELETE policies: lifecycle writes
-- are performed by trusted Backend/operational mechanisms.
CREATE POLICY "Family parents can view device update history"
ON public.device_updates
FOR SELECT
TO authenticated
USING (
    public.is_family_parent(
        public.device_family_id(device_id)
    )
);
