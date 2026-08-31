from __future__ import annotations

from typing import Any

import httpx

from .config import (
    ACCESS_TOKEN_JWT,
    DEVICE_TOKEN,
    FAMILY_BEACON_API_URL,
    FAMILY_BEACON_REQUEST_TIMEOUT,
)


class FamilyBeaconAPI:
    def __init__(
        self,
        base_url: str = FAMILY_BEACON_API_URL,
        device_token: str = DEVICE_TOKEN,
        access_token: str = ACCESS_TOKEN_JWT,
        timeout: float = FAMILY_BEACON_REQUEST_TIMEOUT,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.device_token = device_token
        self.access_token = access_token
        self.timeout = timeout

    def _device_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.device_token}",
        }

    def _user_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.access_token}",
        }

    def authenticate(self) -> dict[str, Any]:
        response = httpx.post(
            f"{self.base_url}/device/auth",
            headers=self._device_headers(),
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def heartbeat(self) -> dict[str, Any]:
        response = httpx.post(
            f"{self.base_url}/device/heartbeat",
            headers=self._device_headers(),
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def claim_command(self) -> dict[str, Any] | None:
        response = httpx.post(
            f"{self.base_url}/device/commands/claim",
            headers=self._device_headers(),
            timeout=self.timeout,
        )
        response.raise_for_status()

        data = response.json()

        if not data:
            return None

        return data
