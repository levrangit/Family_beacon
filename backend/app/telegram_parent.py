from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from app.family_invites import create_family_invite
from app.invite_code import generate_invite_code, hash_invite_code
from app.supabase_client import get_admin_client


class TelegramParentService:
    def __init__(self, admin_client: Any | None = None) -> None:
        self.admin_client = admin_client or get_admin_client()

    def _get_parent_profile(self, telegram_id: int) -> dict[str, Any]:
        response = (
            self.admin_client
            .table("profiles")
            .select("id, display_name, telegram_id, role, is_active")
            .eq("telegram_id", telegram_id)
            .execute()
        )

        profiles = response.data or []
        if not profiles:
            raise ValueError("Parent profile not found")

        profile = profiles[0]
        if profile.get("role") != "parent" or not profile.get("is_active", False):
            raise ValueError("Telegram account is not an active parent")

        return profile

    def _get_family_id(self, profile_id: str) -> str:
        response = (
            self.admin_client
            .table("family_members")
            .select("family_id")
            .eq("profile_id", profile_id)
            .eq("member_type", "parent")
            .order("created_at")
            .limit(1)
            .execute()
        )

        members = response.data or []
        if not members:
            raise ValueError("Family not found")

        return str(members[0]["family_id"])

    def get_profile(self, telegram_id: int) -> dict[str, Any]:
        profile = self._get_parent_profile(telegram_id)

        email: str | None = None
        try:
            user_response = self.admin_client.auth.admin.get_user_by_id(
                str(profile["id"])
            )
            user = getattr(user_response, "user", None)
            email = getattr(user, "email", None) if user is not None else None
        except Exception:
            email = None

        return {
            **profile,
            "email": email,
        }

    def get_family(self, telegram_id: int) -> dict[str, Any]:
        profile = self._get_parent_profile(telegram_id)
        family_id = self._get_family_id(str(profile["id"]))

        family_response = (
            self.admin_client
            .table("families")
            .select("id, name, created_at, updated_at")
            .eq("id", family_id)
            .execute()
        )
        families = family_response.data or []
        if not families:
            raise ValueError("Family not found")

        children_response = (
            self.admin_client
            .table("children")
            .select("id, name, avatar_url, is_active, created_at, updated_at")
            .eq("family_id", family_id)
            .order("created_at")
            .execute()
        )

        return {
            **families[0],
            "children": children_response.data or [],
        }

    def get_children(self, telegram_id: int) -> list[dict[str, Any]]:
        family = self.get_family(telegram_id)
        return family["children"]

    def list_invites(self, telegram_id: int) -> list[dict[str, Any]]:
        profile = self._get_parent_profile(telegram_id)
        family_id = self._get_family_id(str(profile["id"]))

        response = (
            self.admin_client
            .table("family_invites")
            .select("id, family_id, created_by, expires_at, used_at, used_by, revoked_at, created_at")
            .eq("family_id", family_id)
            .order("created_at", desc=True)
            .execute()
        )

        now = datetime.now(timezone.utc)
        result: list[dict[str, Any]] = []

        for invite in response.data or []:
            expires_at = datetime.fromisoformat(str(invite["expires_at"]).replace("Z", "+00:00"))
            if invite.get("revoked_at") is not None:
                status = "revoked"
            elif invite.get("used_at") is not None:
                status = "used"
            elif expires_at <= now:
                status = "expired"
            else:
                status = "active"

            result.append(
                {
                    "invite_id": str(invite["id"]),
                    "expires_at": str(invite["expires_at"]),
                    "used_at": invite.get("used_at"),
                    "revoked_at": invite.get("revoked_at"),
                    "created_at": str(invite["created_at"]),
                    "status": status,
                }
            )

        return result

    def create_child_invite(self, telegram_id: int) -> dict[str, Any]:
        profile = self._get_parent_profile(telegram_id)
        family_id = self._get_family_id(str(profile["id"]))

        code = generate_invite_code()
        code_hash = hash_invite_code(code)
        expires_at = (
            datetime.now(timezone.utc) + timedelta(hours=24)
        ).isoformat()

        response = self.admin_client.table("family_invites").insert(
            {
                "family_id": family_id,
                "created_by": str(profile["id"]),
                "code_hash": code_hash,
                "expires_at": expires_at,
            }
        ).execute()

        invites = response.data or []
        if not invites:
            raise ValueError("Invite could not be created")

        return {
            "invite_id": str(invites[0]["id"]),
            "code": code,
            "expires_at": str(invites[0]["expires_at"]),
        }

    def delete_parent_account(self, telegram_id: int) -> dict[str, str]:
        profile = self._get_parent_profile(telegram_id)
        profile_id = str(profile["id"])

        self.admin_client.rpc(
            "delete_parent_account",
            {"p_profile_id": profile_id},
        ).execute()

        self.admin_client.auth.admin.delete_user(profile_id)

        return {"status": "deleted"}
