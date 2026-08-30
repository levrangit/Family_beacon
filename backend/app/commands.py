from fastapi import HTTPException
from pydantic import BaseModel

from app.supabase_client import get_user_client


class CreateCommandRequest(BaseModel):
    device_id: str
    command: str
    payload: dict = {}


def create_command(
    access_token: str,
    data: CreateCommandRequest,
):
    try:
        client = get_user_client(access_token)

        response = (
            client
            .rpc(
                "create_command",
                {
                    "target_device_id": data.device_id,
                    "target_command": data.command,
                    "target_payload": data.payload,
                },
            )
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=500,
                detail="Failed to create command",
            )

        return response.data

    except HTTPException:
        raise

    except Exception as exc:
        error_message = str(exc)

        if "Permission denied" in error_message:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to create this command",
            )

        if "Device not found" in error_message:
            raise HTTPException(
                status_code=404,
                detail="Device not found",
            )

        raise HTTPException(
            status_code=500,
            detail="Failed to create command",
        )


def list_commands(
    access_token: str,
    device_id: str | None = None,
):
    try:
        client = get_user_client(access_token)

        query = (
            client
            .table("commands")
            .select(
                "id, device_id, command, payload, status, result, "
                "error_message, created_by, created_at, sent_at, "
                "executed_at, updated_at"
            )
            .order("created_at", desc=True)
        )

        if device_id:
            query = query.eq("device_id", device_id)

        response = query.execute()

        return response.data or []

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to load commands",
        )


def get_command(
    access_token: str,
    command_id: str,
):
    try:
        client = get_user_client(access_token)

        response = (
            client
            .table("commands")
            .select(
                "id, device_id, command, payload, status, result, "
                "error_message, created_by, created_at, sent_at, "
                "executed_at, updated_at"
            )
            .eq("id", command_id)
            .limit(1)
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=404,
                detail="Command not found",
            )

        return response.data[0]

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to load command",
        )
