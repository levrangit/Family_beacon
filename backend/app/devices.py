from fastapi import HTTPException
from pydantic import BaseModel

from app.supabase_client import get_user_client


RLS_ERROR_MARKER = "row-level security policy"
DEVICE_NOT_FOUND = "Device not found"


class CreateDeviceRequest(BaseModel):
    child_id: str
    device_id: str
    name: str
    platform: str
    hostname: str | None = None
    agent_version: str | None = None


class UpdateDeviceRequest(BaseModel):
    name: str | None = None
    hostname: str | None = None
    agent_version: str | None = None
    is_online: bool | None = None
    last_seen: str | None = None


def create_device(
    access_token: str,
    data: CreateDeviceRequest,
):
    try:
        client = get_user_client(access_token)

        response = (
            client
            .table("devices")
            .insert(
                {
                    "child_id": data.child_id,
                    "device_id": data.device_id,
                    "name": data.name,
                    "platform": data.platform,
                    "hostname": data.hostname,
                    "agent_version": data.agent_version,
                }
            )
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=500,
                detail="Failed to create device",
            )

        return response.data[0]

    except HTTPException:
        raise

    except Exception as exc:
        error_message = str(exc)

        if RLS_ERROR_MARKER in error_message:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to create this device",
            )

        if "duplicate key" in error_message:
            raise HTTPException(
                status_code=409,
                detail="Device with this device_id already exists",
            )

        raise HTTPException(
            status_code=500,
            detail="Failed to create device",
        )


def list_devices(
    access_token: str,
    child_id: str | None = None,
):
    try:
        client = get_user_client(access_token)

        query = (
            client
            .table("devices")
            .select(
                "id, child_id, device_id, name, platform, "
                "hostname, agent_version, is_online, last_seen, "
                "created_at, updated_at"
            )
        )

        if child_id is not None:
            query = query.eq("child_id", child_id)

        response = (
            query
            .order("created_at")
            .execute()
        )

        return response.data or []

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to load devices",
        )


def get_device(
    access_token: str,
    device_id: str,
):
    try:
        client = get_user_client(access_token)

        response = (
            client
            .table("devices")
            .select(
                "id, child_id, device_id, name, platform, "
                "hostname, agent_version, is_online, last_seen, "
                "created_at, updated_at"
            )
            .eq("id", device_id)
            .execute()
        )

        devices = response.data or []

        if not devices:
            raise HTTPException(
                status_code=404,
                detail=DEVICE_NOT_FOUND,
            )

        return devices[0]

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to load device",
        )


def update_device(
    access_token: str,
    device_id: str,
    data: UpdateDeviceRequest,
):
    try:
        client = get_user_client(access_token)

        updates = data.model_dump(exclude_unset=True)

        if not updates:
            raise HTTPException(
                status_code=400,
                detail="No fields to update",
            )

        response = (
            client
            .table("devices")
            .update(updates)
            .eq("id", device_id)
            .execute()
        )

        devices = response.data or []

        if not devices:
            raise HTTPException(
                status_code=404,
                detail=DEVICE_NOT_FOUND,
            )

        return devices[0]

    except HTTPException:
        raise

    except Exception as exc:
        error_message = str(exc)

        if RLS_ERROR_MARKER in error_message:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to update this device",
            )

        raise HTTPException(
            status_code=500,
            detail="Failed to update device",
        )


def delete_device(
    access_token: str,
    device_id: str,
):
    try:
        client = get_user_client(access_token)

        response = (
            client
            .table("devices")
            .delete()
            .eq("id", device_id)
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=404,
                detail=DEVICE_NOT_FOUND,
            )

        return {
            "deleted": True,
            "device_id": device_id,
        }

    except HTTPException:
        raise

    except Exception as exc:
        error_message = str(exc)

        if RLS_ERROR_MARKER in error_message:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to delete this device",
            )

        raise HTTPException(
            status_code=500,
            detail="Failed to delete device",
        )
