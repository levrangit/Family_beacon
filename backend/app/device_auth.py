import hashlib

from fastapi import Header, HTTPException
from pydantic import BaseModel

from app.supabase_client import supabase


TOKEN_PREFIX = "fb_dev_"
DEVICE_AUTH_REQUIRED = "Device authorization is required"


class DeviceAuthRequest(BaseModel):
    token: str


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
