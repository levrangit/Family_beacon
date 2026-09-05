from fastapi import Header, HTTPException
from pydantic import BaseModel, ConfigDict, field_validator

from app.device_auth import get_device_token_hash
from app.supabase_client import supabase


class DeviceHeartbeatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    agent_version: str

    @field_validator("agent_version")
    @classmethod
    def validate_agent_version(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Agent version is required")
        if len(value) > 64:
            raise ValueError("Agent version is too long")
        return value


def device_heartbeat(
    data: DeviceHeartbeatRequest,
    authorization: str | None = Header(default=None),
):
    token_hash = get_device_token_hash(authorization)

    if supabase is None:
        raise HTTPException(
            status_code=500,
            detail="Supabase configuration is missing",
        )

    try:
        response = (
            supabase
            .rpc(
                "device_heartbeat_by_token_v2",
                {
                    "target_token_hash": token_hash,
                    "reported_agent_version": data.agent_version,
                },
            )
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=401,
                detail="Invalid device token",
            )

        return response.data

    except HTTPException:
        raise

    except Exception as exc:
        error_message = str(exc)

        if "Invalid device token" in error_message:
            raise HTTPException(
                status_code=401,
                detail="Invalid device token",
            )

        if "Agent version is required" in error_message:
            raise HTTPException(
                status_code=422,
                detail="Agent version is required",
            )

        if "Device token is required" in error_message:
            raise HTTPException(
                status_code=401,
                detail="Device token is required",
            )

        if "Device not found" in error_message:
            raise HTTPException(
                status_code=404,
                detail="Device not found",
            )

        raise HTTPException(
            status_code=500,
            detail="Device heartbeat failed",
        )
