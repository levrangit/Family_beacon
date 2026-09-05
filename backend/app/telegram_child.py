from __future__ import annotations

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
