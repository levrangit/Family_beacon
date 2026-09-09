"""Minimal synchronous Backend client used by the Device Agent Service."""

from __future__ import annotations

from datetime import datetime
import json
from urllib import error, request


class BackendClientError(RuntimeError):
    """Raised when the Backend cannot complete a registration request."""


class BackendClient:
    def __init__(self, base_url: str, timeout: float = 15.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def bootstrap_agent_installation(
        self,
        *,
        installation_code: str,
        agent_secret: str,
        platform: str,
        device_id: str,
        hostname: str | None,
        agent_version: str | None,
    ) -> dict:
        return self._post(
            "/agent-installations/bootstrap",
            {
                "installation_code": installation_code,
                "agent_secret": agent_secret,
                "platform": platform,
                "device_id": device_id,
                "hostname": hostname,
                "agent_version": agent_version,
            },
        )

    def create_device_registration_request(
        self,
        *,
        platform: str,
        device_id: str,
        hostname: str | None,
        agent_version: str | None,
    ) -> dict:
        return self._post(
            "/device-registration/requests",
            {
                "device": {
                    "platform": platform,
                    "device_id": device_id,
                    "hostname": hostname,
                    "agent_version": agent_version,
                }
            },
        )

    def get_device_registration_request(self, request_id: str) -> dict:
        return self._request("GET", f"/device-registration/requests/{request_id}")

    def cancel_device_registration_request(self, request_id: str) -> dict:
        return self._post(
            "/device-registration/cancel",
            {"request_id": request_id},
        )

    def _post(self, path: str, payload: dict) -> dict:
        body = json.dumps(payload).encode("utf-8")
        return self._request(
            "POST",
            path,
            body=body,
            headers={"Content-Type": "application/json"},
        )

    def _request(
        self,
        method: str,
        path: str,
        *,
        body: bytes | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict:
        http_request = request.Request(
            f"{self.base_url}{path}",
            data=body,
            headers=headers or {},
            method=method,
        )
        try:
            with request.urlopen(http_request, timeout=self.timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            try:
                detail = json.loads(exc.read().decode("utf-8"))
            except (ValueError, UnicodeDecodeError):
                detail = {"detail": str(exc)}
            raise BackendClientError(
                f"Backend request failed with HTTP {exc.code}: {detail}"
            ) from exc
        except (error.URLError, TimeoutError, OSError) as exc:
            raise BackendClientError("Backend request failed") from exc

        if not isinstance(payload, dict):
            raise BackendClientError("Backend returned an invalid response")
        return payload


def parse_backend_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))
