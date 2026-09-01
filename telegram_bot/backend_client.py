from __future__ import annotations

from typing import Any


class BackendClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")

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
