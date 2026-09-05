from typing import Literal

from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict

from app.supabase_client import get_admin_client, get_user_client


Platform = Literal["windows", "macos", "linux"]


class CreateCompatibilityRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    release_id: str
    platform: Platform
    min_agent_version: str | None = None
    max_agent_version: str | None = None


def list_compatibility(access_token: str):
    try:
        client = get_user_client(access_token)
        response = (
            client
            .table("component_compatibility")
            .select(
                "id, release_id, platform, min_agent_version, "
                "max_agent_version, created_at, updated_at"
            )
            .order("created_at")
            .execute()
        )
        return response.data or []
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Failed to load component compatibility",
        ) from exc


def create_compatibility(data: CreateCompatibilityRequest):
    """Create compatibility through the trusted service-role client only."""
    try:
        client = get_admin_client()
        response = (
            client
            .table("component_compatibility")
            .insert(
                {
                    "release_id": data.release_id,
                    "platform": data.platform,
                    "min_agent_version": data.min_agent_version,
                    "max_agent_version": data.max_agent_version,
                }
            )
            .execute()
        )

        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to create component compatibility")

        return response.data[0]
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Failed to create component compatibility",
        ) from exc
