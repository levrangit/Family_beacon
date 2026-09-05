-- ============================================================
-- Family Beacon
-- Migration: 029_component_releases
-- Database: Supabase PostgreSQL
--
-- PR3: catalog published component releases.
-- ============================================================

CREATE TABLE public.component_releases (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),

    component text NOT NULL
        CHECK (length(trim(component)) > 0),

    version text NOT NULL
        CHECK (version ~ '^[0-9]+\.[0-9]+\.[0-9]+$'),

    artifact_ref text NOT NULL
        CHECK (length(trim(artifact_ref)) > 0),

    checksum text NOT NULL
        CHECK (length(trim(checksum)) > 0),

    release_notes text,

    published_at timestamptz NOT NULL DEFAULT now(),

    created_at timestamptz NOT NULL DEFAULT now(),

    updated_at timestamptz NOT NULL DEFAULT now(),

    CONSTRAINT component_releases_component_version_key
        UNIQUE (component, version)
);

CREATE INDEX component_releases_component_published_idx
    ON public.component_releases(component, published_at DESC);

CREATE INDEX component_releases_component_version_idx
    ON public.component_releases(component, version);

CREATE TRIGGER component_releases_set_updated_at
BEFORE UPDATE ON public.component_releases
FOR EACH ROW
EXECUTE FUNCTION public.set_updated_at();

ALTER TABLE public.component_releases ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Authenticated users can view component releases"
ON public.component_releases
FOR SELECT
TO authenticated
USING (true);
