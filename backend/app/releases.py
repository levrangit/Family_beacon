from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict

from app.supabase_client import get_admin_client, get_user_client


RELEASE_NOT_FOUND = "Component release not found"


class CreateReleaseRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    component: str
    version: str
    artifact_ref: str
    checksum: str
    release_notes: str | None = None


def list_releases(access_token: str):
    try:
        client = get_user_client(access_token)
        response = (
            client
            .table("component_releases")
            .select(
                "id, component, version, artifact_ref, checksum, "
                "release_notes, published_at, created_at, updated_at"
            )
            .order("published_at", desc=True)
            .execute()
        )
        return response.data or []
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Failed to load component releases",
        ) from exc


def get_release(access_token: str, release_id: str):
    try:
        client = get_user_client(access_token)
        response = (
            client
            .table("component_releases")
            .select(
                "id, component, version, artifact_ref, checksum, "
                "release_notes, published_at, created_at, updated_at"
            )
            .eq("id", release_id)
            .maybe_single()
            .execute()
        )

        if response.data is None:
            raise HTTPException(status_code=404, detail=RELEASE_NOT_FOUND)

        return response.data
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Failed to load component release",
        ) from exc


def create_release(data: CreateReleaseRequest):
    """Create a release through the trusted service-role client only."""
    try:
        client = get_admin_client()
        response = (
            client
            .table("component_releases")
            .insert(
                {
                    "component": data.component,
                    "version": data.version,
                    "artifact_ref": data.artifact_ref,
                    "checksum": data.checksum,
                    "release_notes": data.release_notes,
                }
            )
            .execute()
        )

        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to create component release")

        return response.data[0]
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Failed to create component release",
        ) from exc
