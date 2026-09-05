from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.invite_code import hash_invite_code
from app.supabase_client import get_admin_client


class TelegramChildService:
    def __init__(self, admin_client: Any | None = None) -> None:
        self.admin_client = admin_client or get_admin_client()

    def register_child(
        self,
        telegram_id: int,
        invite_code: str,
        child_name: str,
    ) -> dict[str, Any]:
        if not invite_code.strip():
            raise ValueError("Invite code is required")

        if not child_name.strip():
            raise ValueError("Child name is required")

        code_hash = hash_invite_code(invite_code.strip().upper())

        response = self.admin_client.rpc(
            "register_child_by_invite",
            {
                "p_code_hash": code_hash,
                "p_telegram_id": telegram_id,
                "p_child_name": child_name.strip(),
            },
        ).execute()

        rows = response.data or []
        if not rows:
            raise ValueError("Child registration failed")

        row = rows[0]
        return {
            "child_id": str(row["child_id"]),
            "family_id": str(row["family_id"]),
            "invite_id": str(row["invite_id"]),
        }

    def get_dashboard(self, telegram_id: int) -> dict[str, Any]:
        child_response = (
            self.admin_client
            .table("children")
            .select("id, family_id, name, avatar_url, telegram_id, is_active")
            .eq("telegram_id", telegram_id)
            .execute()
        )

        children = child_response.data or []
        if not children:
            raise ValueError("Child not found")

        child = children[0]
        child_id = child["id"]

        devices_response = (
            self.admin_client
            .table("devices")
            .select(
                "id, child_id, device_id, name, platform, hostname, "
                "agent_version, is_online, last_seen"
            )
            .eq("child_id", child_id)
            .order("created_at")
            .execute()
        )

        today = datetime.now(timezone.utc).date()
        usage_response = (
            self.admin_client
            .table("time_usage")
            .select("used_minutes")
            .eq("child_id", child_id)
            .eq("usage_date", today.isoformat())
            .execute()
        )

        used_minutes = sum(
            int(row.get("used_minutes") or 0)
            for row in (usage_response.data or [])
        )

        # PostgreSQL EXTRACT(DOW) uses Sunday=0 ... Saturday=6.
        day_of_week = (today.weekday() + 1) % 7
        policy_response = (
            self.admin_client
            .table("time_policies")
            .select(
                "daily_limit_minutes, start_time, end_time, is_enabled"
            )
            .eq("child_id", child_id)
            .eq("day_of_week", day_of_week)
            .maybe_single()
            .execute()
        )

        return {
            "child": child,
            "devices": devices_response.data or [],
            "today_usage": {"used_minutes": used_minutes},
            "today_policy": policy_response.data,
        }
