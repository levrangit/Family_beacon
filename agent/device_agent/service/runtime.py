"""Runtime lifecycle for the Family Beacon Device Agent Windows Service."""

from __future__ import annotations

import threading
from typing import Any

from ..backend_client import BackendClient, BackendClientError, parse_backend_datetime
from ..config import load_config
from ..identity import collect_identity
from ..ipc.named_pipe_server import NamedPipeIPCServer
from ..ipc.protocol import REGISTRATION_CANCEL, REGISTRATION_START, STATUS
from ..logging import setup_logging
from ..registration import RegistrationCoordinator


class AgentRuntime:
    """Own the Device Agent service runtime independently of Windows SCM."""

    def __init__(self, backend_client: BackendClient | None = None) -> None:
        self.config = load_config()
        self.logger = setup_logging(self.config.log_level)
        self._stop_event = threading.Event()
        self.registration = RegistrationCoordinator()
        self.backend = backend_client or BackendClient(self.config.backend_url)
        self.ipc_server: NamedPipeIPCServer | None = None
        self._identity = None

    def start(self) -> None:
        """Start identity initialization and the local IPC service."""
        self.logger.info(
            "Starting Device Agent runtime %s",
            self.config.agent_version,
        )

        self._identity = collect_identity(self.config.agent_version)
        self.logger.info(
            "Identity collected: platform=%s hostname=%s username=%s session=%s",
            self._identity.platform,
            self._identity.hostname,
            self._identity.os_username,
            self._identity.os_session_identity,
        )

        if self.ipc_server is None:
            self.ipc_server = NamedPipeIPCServer(self.handle_ipc_request)
            self.ipc_server.start()
            self.logger.info("Device Agent IPC listening on %s", self.ipc_server.endpoint)

    def run(self) -> None:
        """Keep the runtime alive until a stop request is received."""
        self.start()
        self._stop_event.wait()
        self.stop()

    def request_stop(self) -> None:
        """Request graceful runtime shutdown."""
        self._stop_event.set()

    def stop(self) -> None:
        """Stop IPC and release currently owned resources."""
        if self.ipc_server is not None:
            self.ipc_server.stop()
            self.ipc_server = None

        if not self._stop_event.is_set():
            self._stop_event.set()

        self.logger.info(
            "Device Agent runtime %s stopped",
            self.config.agent_version,
        )

    def handle_ipc_request(self, request: dict[str, Any]) -> dict[str, Any]:
        """Handle local Tray requests and use Backend as registration authority."""
        message_type = request.get("type")

        if message_type == STATUS:
            active_request = self.registration.request
            return {
                "ok": True,
                "type": STATUS,
                "service": "running",
                "registration_active": active_request is not None,
            }

        if message_type == REGISTRATION_START:
            if self._identity is None:
                self._identity = collect_identity(self.config.agent_version)

            try:
                payload = self.backend.create_device_registration_request(
                    platform=self._identity.platform,
                    device_id=self._identity.windows_machine_guid,
                    hostname=self._identity.hostname,
                    agent_version=self.config.agent_version,
                )
                registration = self.registration.set_request(
                    request_id=str(payload["request_id"]),
                    registration_code=str(payload["registration_code"]),
                    expires_at=parse_backend_datetime(str(payload["expires_at"])),
                )
            except (BackendClientError, KeyError, TypeError, ValueError) as exc:
                self.logger.warning("Device registration start failed: %s", exc)
                return {
                    "ok": False,
                    "type": REGISTRATION_START,
                    "error": "registration_backend_unavailable",
                }

            return {
                "ok": True,
                "type": REGISTRATION_START,
                "request_id": registration.request_id,
                "registration_code": registration.registration_code,
                "expires_at": registration.expires_at.isoformat(),
            }

        if message_type == REGISTRATION_CANCEL:
            active_request = self.registration.request
            if active_request is not None:
                try:
                    self.backend.cancel_device_registration_request(active_request.request_id)
                except BackendClientError as exc:
                    self.logger.warning("Device registration cancel failed: %s", exc)
                    return {
                        "ok": False,
                        "type": REGISTRATION_CANCEL,
                        "error": "registration_backend_unavailable",
                    }
            self.registration.cancel()
            return {"ok": True, "type": REGISTRATION_CANCEL}

        return {"ok": False, "error": "unsupported_message_type"}
