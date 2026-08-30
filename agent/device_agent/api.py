import requests

from .config import BACKEND_URL, DEVICE_TOKEN


class DeviceAgentAPI:
    def __init__(
        self,
        backend_url: str = BACKEND_URL,
        device_token: str = DEVICE_TOKEN,
    ):
        self.backend_url = backend_url.rstrip("/")
        self.device_token = device_token

    def _headers(self) -> dict[str, str]:
        if not self.device_token:
            raise RuntimeError("Device token is not configured")

        return {
            "Authorization": f"Bearer {self.device_token}",
            "Content-Type": "application/json",
        }

    def authenticate(self) -> dict:
        response = requests.post(
            f"{self.backend_url}/device/auth",
            json={"token": self.device_token},
            timeout=10,
        )

        response.raise_for_status()
        return response.json()

    def claim_command(self):
        response = requests.post(
            f"{self.backend_url}/device/commands/claim",
            headers=self._headers(),
            timeout=10,
        )

        response.raise_for_status()

        if not response.content:
            return None

        data = response.json()

        if not data:
            return None

        if isinstance(data, list):
            if not data:
                return None
            data = data[0]

        if not isinstance(data, dict):
            raise RuntimeError(
                "Invalid claim command response format"
            )

        if data.get("id") is None:
            return None

        return data

    def complete_command(
        self,
        command_id: str,
        status: str,
        result: dict | None = None,
        error_message: str | None = None,
    ) -> dict:
        response = requests.post(
            f"{self.backend_url}/device/commands/{command_id}/complete",
            headers=self._headers(),
            json={
                "status": status,
                "result": result,
                "error_message": error_message,
            },
            timeout=10,
        )

        response.raise_for_status()
        return response.json()
