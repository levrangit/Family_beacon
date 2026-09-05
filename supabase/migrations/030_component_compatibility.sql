-- ============================================================
-- Family Beacon
-- Migration: 030_component_compatibility
-- Database: Supabase PostgreSQL
--
-- PR3: describe which device platforms and agent versions can
-- use a published component release.
-- ============================================================

CREATE TABLE public.component_compatibility (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),

    release_id uuid NOT NULL
        REFERENCES public.component_releases(id)
        ON DELETE CASCADE,

    platform public.device_platform NOT NULL,

    min_agent_version text
        CHECK (
            min_agent_version IS NULL
            OR min_agent_version ~ '^[0-9]+\.[0-9]+\.[0-9]+$'
        ),

    max_agent_version text
        CHECK (
            max_agent_version IS NULL
            OR max_agent_version ~ '^[0-9]+\.[0-9]+\.[0-9]+$'
        ),

    created_at timestamptz NOT NULL DEFAULT now(),

    updated_at timestamptz NOT NULL DEFAULT now(),

    CONSTRAINT component_compatibility_release_platform_key
        UNIQUE (release_id, platform)
);

CREATE INDEX component_compatibility_platform_idx
    ON public.component_compatibility(platform);

CREATE TRIGGER component_compatibility_set_updated_at
BEFORE UPDATE ON public.component_compatibility
FOR EACH ROW
EXECUTE FUNCTION public.set_updated_at();

ALTER TABLE public.component_compatibility ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Authenticated users can view component compatibility"
ON public.component_compatibility
FOR SELECT
TO authenticated
USING (true);
