from __future__ import annotations

from typing import Any

import httpx


class BackendClient:
    def __init__(self, base_url: str, shared_secret: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.shared_secret = shared_secret

    async def lookup_telegram_id(self, telegram_id: int) -> dict[str, Any] | None:
        headers = {"X-Telegram-Bot-Key": self.shared_secret}

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{self.base_url}/telegram/lookup/{telegram_id}",
                headers=headers,
            )

        if response.status_code == 404:
            return None

        response.raise_for_status()
        return response.json()

    def register_parent(
        self,
        telegram_id: int,
        login: str,
        password: str,
    ) -> dict[str, Any]:
        return {
            "telegram_id": telegram_id,
            "login": login,
            "password": password,
        }
