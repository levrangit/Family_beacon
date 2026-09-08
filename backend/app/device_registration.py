from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib

from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict

from app.supabase_client import get_admin_client


REGISTRATION_TTL_MINUTES = 10


class DeviceRegistrationDevice(BaseModel):
    model_config = ConfigDict(extra="forbid")

    platform: str
    device_id: str
    hostname: str | None = None
    agent_version: str | None = None


class CreateDeviceRegistrationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    child_id: str
    registration_code: str
    device: DeviceRegistrationDevice


class SubmitDeviceRegistrationCodeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    telegram_id: int
    registration_code: str


def _hash_registration_code(registration_code: str) -> str:
    normalized_code = registration_code.strip().upper()
    if not normalized_code:
        raise HTTPException(status_code=422, detail="Registration code is required")
    return hashlib.sha256(normalized_code.encode("utf-8")).hexdigest()


def create_device_registration_request(
    data: CreateDeviceRegistrationRequest,
):
    if data.device.platform not in {"windows", "macos", "linux"}:
        raise HTTPException(status_code=422, detail="Unsupported device platform")

    code_hash = _hash_registration_code(data.registration_code)
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=REGISTRATION_TTL_MINUTES)

    try:
        client = get_admin_client()
        response = (
            client
            .table("device_registration_requests")
            .insert(
                {
                    "child_id": data.child_id,
                    "request_code_hash": code_hash,
                    "status": "pending",
                    "device_platform": data.device.platform,
                    "device_id": data.device.device_id,
                    "hostname": data.device.hostname,
                    "agent_version": data.device.agent_version,
                    "expires_at": expires_at.isoformat(),
                }
            )
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=500,
                detail="Failed to create device registration request",
            )

        request = response.data[0]
        return {
            "request_id": request["id"],
            "status": request["status"],
            "expires_at": request["expires_at"],
        }

    except HTTPException:
        raise
    except Exception as exc:
        error_message = str(exc)

        if "duplicate key" in error_message:
            raise HTTPException(
                status_code=409,
                detail="Registration code is already in use",
            ) from exc

        if "configuration is missing" in error_message.lower():
            raise HTTPException(
                status_code=503,
                detail="Supabase configuration is missing",
            ) from exc

        raise HTTPException(
            status_code=500,
            detail="Failed to create device registration request",
        ) from exc


def submit_device_registration_code(
    data: SubmitDeviceRegistrationCodeRequest,
):
    code_hash = _hash_registration_code(data.registration_code)
    now = datetime.now(timezone.utc)

    try:
        client = get_admin_client()

        child_response = (
            client
            .table("children")
            .select("id")
            .eq("telegram_id", data.telegram_id)
            .eq("is_active", True)
            .limit(1)
            .execute()
        )

        children = child_response.data or []
        if not children:
            raise HTTPException(status_code=404, detail="Child not found")

        child_id = children[0]["id"]

        request_response = (
            client
            .table("device_registration_requests")
            .select("id, child_id, status, expires_at")
            .eq("request_code_hash", code_hash)
            .eq("child_id", child_id)
            .limit(1)
            .execute()
        )

        requests = request_response.data or []
        if not requests:
            raise HTTPException(
                status_code=404,
                detail="Device registration code not found",
            )

        request = requests[0]
        if request["status"] != "pending":
            raise HTTPException(
                status_code=409,
                detail="Device registration request is not pending",
            )

        expires_at = datetime.fromisoformat(
            request["expires_at"].replace("Z", "+00:00")
        )
        if expires_at <= now:
            (
                client
                .table("device_registration_requests")
                .update(
                    {
                        "status": "expired",
                    }
                )
                .eq("id", request["id"])
                .eq("status", "pending")
                .execute()
            )
            raise HTTPException(
                status_code=410,
                detail="Device registration code has expired",
            )

        return {
            "request_id": request["id"],
            "child_id": request["child_id"],
            "status": request["status"],
            "expires_at": request["expires_at"],
        }

    except HTTPException:
        raise
    except Exception as exc:
        if "configuration is missing" in str(exc).lower():
            raise HTTPException(
                status_code=503,
                detail="Supabase configuration is missing",
            ) from exc

        raise HTTPException(
            status_code=500,
            detail="Failed to submit device registration code",
        ) from exc
