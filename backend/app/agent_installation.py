from __future__ import annotations

from datetime import datetime, timedelta, timezone
from hashlib import sha256
import secrets
from typing import Any

from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict

from app.code import generate_code, hash_code
from app.supabase_client import get_admin_client


INSTALLATION_TTL_MINUTES = 30
AGENT_SECRET_PREFIX = "fb_agent_"


class CreateAgentInstallationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    telegram_id: int


class BootstrapAgentInstallationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    installation_code: str
    agent_secret: str
    platform: str
    device_id: str
    hostname: str | None = None
    agent_version: str | None = None


def generate_agent_secret() -> str:
    return AGENT_SECRET_PREFIX + secrets.token_urlsafe(32)


def hash_agent_secret(agent_secret: str) -> str:
    if not agent_secret:
        raise HTTPException(status_code=422, detail="Agent secret is required")
    return sha256(agent_secret.encode("utf-8")).hexdigest()


def create_agent_installation(data: CreateAgentInstallationRequest):
    if not data.telegram_id:
        raise HTTPException(status_code=422, detail="Telegram ID is required")

    code = generate_code()
    code_hash = hash_code(code)
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=INSTALLATION_TTL_MINUTES)

    try:
        client = get_admin_client()

        profile_response = (
            client
            .table("profiles")
            .select("id, role, is_active")
            .eq("telegram_id", data.telegram_id)
            .limit(1)
            .execute()
        )
        profiles = profile_response.data or []
        if not profiles:
            raise HTTPException(status_code=404, detail="Parent profile not found")

        profile = profiles[0]
        if profile.get("role") != "parent" or not profile.get("is_active", False):
            raise HTTPException(status_code=403, detail="Telegram account is not an active parent")

        family_response = (
            client
            .table("family_members")
            .select("family_id")
            .eq("profile_id", str(profile["id"]))
            .eq("member_type", "parent")
            .order("created_at")
            .limit(1)
            .execute()
        )
        members = family_response.data or []
        if not members:
            raise HTTPException(status_code=404, detail="Family not found")

        family_id = str(members[0]["family_id"])
        response = (
            client
            .table("agent_installations")
            .insert(
                {
                    "family_id": family_id,
                    "installation_code_hash": code_hash,
                    "status": "pending",
                    "expires_at": expires_at.isoformat(),
                }
            )
            .execute()
        )

        installations = response.data or []
        if not installations:
            raise HTTPException(status_code=500, detail="Failed to create Agent installation")

        installation = installations[0]
        return {
            "installation_id": installation["id"],
            "installation_code": code,
            "status": installation["status"],
            "expires_at": installation["expires_at"],
        }

    except HTTPException:
        raise
    except Exception as exc:
        message = str(exc)
        if "configuration is missing" in message.lower():
            raise HTTPException(status_code=503, detail="Supabase configuration is missing") from exc
        if "duplicate key" in message:
            raise HTTPException(status_code=409, detail="Installation code is already in use") from exc
        raise HTTPException(status_code=500, detail="Failed to create Agent installation") from exc


def bootstrap_agent_installation(data: BootstrapAgentInstallationRequest):
    if data.platform not in {"windows", "macos", "linux"}:
        raise HTTPException(status_code=422, detail="Unsupported device platform")
    if not data.device_id.strip():
        raise HTTPException(status_code=422, detail="Device ID is required")
    if not data.agent_secret.startswith(AGENT_SECRET_PREFIX):
        raise HTTPException(status_code=422, detail="Invalid Agent secret")

    code_hash = hash_code(data.installation_code.strip().upper())
    secret_hash = hash_agent_secret(data.agent_secret)
    now = datetime.now(timezone.utc)

    try:
        client = get_admin_client()
        response = (
            client
            .table("agent_installations")
            .select("id, family_id, status, expires_at")
            .eq("installation_code_hash", code_hash)
            .limit(1)
            .execute()
        )
        installations = response.data or []
        if not installations:
            raise HTTPException(status_code=404, detail="Installation code not found")

        installation = installations[0]
        expires_at = datetime.fromisoformat(
            str(installation["expires_at"]).replace("Z", "+00:00")
        )
        if expires_at <= now:
            client.table("agent_installations").update({"status": "expired"}).eq(
                "id", installation["id"]
            ).eq("status", "pending").execute()
            raise HTTPException(status_code=410, detail="Installation code has expired")

        if installation["status"] != "pending":
            raise HTTPException(status_code=409, detail="Installation code is already used")

        claimed = (
            client
            .table("agent_installations")
            .update(
                {
                    "agent_secret_hash": secret_hash,
                    "status": "claimed",
                    "device_platform": data.platform,
                    "device_id": data.device_id,
                    "hostname": data.hostname,
                    "agent_version": data.agent_version,
                    "claimed_at": now.isoformat(),
                }
            )
            .eq("id", installation["id"])
            .eq("status", "pending")
            .execute()
        )
        rows = claimed.data or []
        if not rows:
            raise HTTPException(status_code=409, detail="Installation code is already used")

        return {
            "installation_id": rows[0]["id"],
            "family_id": rows[0]["family_id"],
            "status": rows[0]["status"],
        }

    except HTTPException:
        raise
    except Exception as exc:
        if "configuration is missing" in str(exc).lower():
            raise HTTPException(status_code=503, detail="Supabase configuration is missing") from exc
        raise HTTPException(status_code=500, detail="Failed to bootstrap Agent installation") from exc
