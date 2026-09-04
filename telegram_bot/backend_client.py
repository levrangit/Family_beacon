from __future__ import annotations

from typing import Any

import httpx


class BackendClient:
    def __init__(self, base_url: str, shared_secret: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.shared_secret = shared_secret

    def _headers(self) -> dict[str, str]:
        return {"X-Telegram-Bot-Key": self.shared_secret}

    async def lookup_telegram_id(self, telegram_id: int) -> dict[str, Any] | None:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{self.base_url}/telegram/lookup/{telegram_id}",
                headers=self._headers(),
            )
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()

    async def register_parent(
        self,
        telegram_id: int,
        login: str,
        password: str,
    ) -> dict[str, Any]:
        payload = {
            "telegram_id": telegram_id,
            "login": login,
            "password": password,
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                f"{self.base_url}/auth/register-parent",
                json=payload,
                headers=self._headers(),
            )

        response.raise_for_status()
        return response.json()

    async def get_parent_profile(self, telegram_id: int) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{self.base_url}/telegram/parent/profile/{telegram_id}",
                headers=self._headers(),
            )
        response.raise_for_status()
        return response.json()

    async def get_parent_family(self, telegram_id: int) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{self.base_url}/telegram/parent/family/{telegram_id}",
                headers=self._headers(),
            )
        response.raise_for_status()
        return response.json()

    async def get_parent_children(self, telegram_id: int) -> list[dict[str, Any]]:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{self.base_url}/telegram/parent/children/{telegram_id}",
                headers=self._headers(),
            )
        response.raise_for_status()
        return response.json()

    async def list_parent_invites(self, telegram_id: int) -> list[dict[str, Any]]:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{self.base_url}/telegram/parent/invites/{telegram_id}",
                headers=self._headers(),
            )
        response.raise_for_status()
        return response.json()

    async def create_parent_invite(self, telegram_id: int) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                f"{self.base_url}/telegram/parent/invites/{telegram_id}",
                headers=self._headers(),
            )
        response.raise_for_status()
        return response.json()

    async def delete_parent_account(self, telegram_id: int) -> dict[str, str]:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.delete(
                f"{self.base_url}/telegram/parent/account/{telegram_id}",
                headers=self._headers(),
            )
        response.raise_for_status()
        return response.json()
