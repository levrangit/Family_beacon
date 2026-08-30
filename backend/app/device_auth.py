import hashlib
import secrets

from fastapi import Header, HTTPException
from pydantic import BaseModel

from app.supabase_client import get_user_client, supabase


TOKEN_PREFIX = "fb_dev_"
DEVICE_AUTH_REQUIRED = "Device authorization is required"


class DeviceAuthRequest(BaseModel):
    token: str


def create_device_auth_token(
    access_token: str,
    device_id: str,
):
    if not access_token:
        raise HTTPException(
            status_code=401,
            detail="User authorization is required",
        )

    if not device_id:
        raise HTTPException(
            status_code=400,
            detail="Device ID is required",
        )

    token = TOKEN_PREFIX + secrets.token_urlsafe(32)

    token_hash = hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()

    try:
        client = get_user_client(access_token)

        response = (
            client
            .rpc(
                "create_device_auth_token",
                {
                    "target_device_id": device_id,
                    "target_token_hash": token_hash,
                },
            )
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=500,
                detail="Failed to create device auth token",
            )

        return {
            "device_id": device_id,
            "token": token,
        }

    except HTTPException:
        raise

    except Exception as exc:
        error_message = str(exc)

        if "Permission denied" in error_message:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to create a device token",
            )

        if "Device not found" in error_message:
            raise HTTPException(
                status_code=404,
                detail="Device not found",
            )

        raise HTTPException(
            status_code=500,
            detail="Failed to create device auth token",
        )


def authenticate_device_token(
    authorization: str | None = Header(default=None),
) -> str:
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail=DEVICE_AUTH_REQUIRED,
        )

    scheme, _, token = authorization.partition(" ")

    if scheme.lower() != "bearer" or not token:
        raise HTTPException(
            status_code=401,
            detail="Invalid device authorization",
        )

    if not token.startswith(TOKEN_PREFIX):
        raise HTTPException(
            status_code=401,
            detail="Invalid device token",
        )

    if supabase is None:
        raise HTTPException(
            status_code=500,
            detail="Supabase configuration is missing",
        )

    token_hash = hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()

    try:
        response = (
            supabase
            .rpc(
                "authenticate_device",
                {
                    "target_token_hash": token_hash,
                },
            )
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=401,
                detail="Invalid device token",
            )

        return str(response.data)

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Device authentication failed",
        )


def authenticate_device(token: str):
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Device token is required",
        )

    if not token.startswith(TOKEN_PREFIX):
        raise HTTPException(
            status_code=401,
            detail="Invalid device token",
        )

    if supabase is None:
        raise HTTPException(
            status_code=500,
            detail="Supabase configuration is missing",
        )

    token_hash = hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()

    try:
        response = (
            supabase
            .rpc(
                "authenticate_device",
                {
                    "target_token_hash": token_hash,
                },
            )
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=401,
                detail="Invalid device token",
            )

        return {
            "device_id": str(response.data),
        }

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Device authentication failed",
        )


def claim_next_device_command(
    authorization: str | None = None,
):
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail=DEVICE_AUTH_REQUIRED,
        )

    scheme, _, token = authorization.partition(" ")

    if scheme.lower() != "bearer" or not token:
        raise HTTPException(
            status_code=401,
            detail="Invalid device authorization",
        )

    if not token.startswith(TOKEN_PREFIX):
        raise HTTPException(
            status_code=401,
            detail="Invalid device token",
        )

    if supabase is None:
        raise HTTPException(
            status_code=500,
            detail="Supabase configuration is missing",
        )

    token_hash = hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()

    try:
        response = (
            supabase
            .rpc(
                "claim_next_device_command",
                {
                    "target_token_hash": token_hash,
                },
            )
            .execute()
        )

        if not response.data:
            return None

        return response.data

    except Exception as exc:
        error_message = str(exc)

        if "Invalid device token" in error_message:
            raise HTTPException(
                status_code=401,
                detail="Invalid device token",
            )

        raise HTTPException(
            status_code=500,
            detail="Failed to claim device command",
        )


def complete_device_command(
    authorization: str | None,
    command_id: str,
    status: str,
    result: dict | None = None,
    error_message: str | None = None,
):
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail=DEVICE_AUTH_REQUIRED,
        )

    scheme, _, token = authorization.partition(" ")

    if scheme.lower() != "bearer" or not token:
        raise HTTPException(
            status_code=401,
            detail="Invalid device authorization",
        )

    if not token.startswith(TOKEN_PREFIX):
        raise HTTPException(
            status_code=401,
            detail="Invalid device token",
        )

    if supabase is None:
        raise HTTPException(
            status_code=500,
            detail="Supabase configuration is missing",
        )

    token_hash = hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()

    try:
        response = (
            supabase
            .rpc(
                "complete_device_command",
                {
                    "target_token_hash": token_hash,
                    "target_command_id": command_id,
                    "target_status": status,
                    "target_result": result,
                    "target_error_message": error_message,
                },
            )
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=404,
                detail="Command not found or not executable",
            )

        return response.data

    except HTTPException:
        raise

    except Exception as exc:
        error_message_text = str(exc)

        if "Invalid device token" in error_message_text:
            raise HTTPException(
                status_code=401,
                detail="Invalid device token",
            )

        if "Invalid command status" in error_message_text:
            raise HTTPException(
                status_code=400,
                detail="Invalid command status",
            )

        if "Command not found or not executable" in error_message_text:
            raise HTTPException(
                status_code=404,
                detail="Command not found or not executable",
            )

        raise HTTPException(
            status_code=500,
            detail="Failed to complete device command",
        )
