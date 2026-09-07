"""Runtime lifecycle for the Family Beacon Device Agent Windows Service."""

from __future__ import annotations

import threading
from typing import Any

from ..config import load_config
from ..identity import collect_identity
from ..ipc.named_pipe_server import NamedPipeIPCServer
from ..ipc.protocol import REGISTRATION_CANCEL, REGISTRATION_START, STATUS
from ..logging import setup_logging
from ..registration import RegistrationCoordinator


class AgentRuntime:
    """Own the Device Agent service runtime independently of Windows SCM."""

    def __init__(self) -> None:
        self.config = load_config()
        self.logger = setup_logging(self.config.log_level)
        self._stop_event = threading.Event()
        self.registration = RegistrationCoordinator()
        self.ipc_server: NamedPipeIPCServer | None = None

    def start(self) -> None:
        """Start identity initialization and the local IPC service."""
        self.logger.info(
            "Starting Device Agent runtime %s",
            self.config.agent_version,
        )

        identity = collect_identity(self.config.agent_version)
        self.logger.info(
            "Identity collected: platform=%s hostname=%s username=%s session=%s",
            identity.platform,
            identity.hostname,
            identity.os_username,
            identity.os_session_identity,
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
        """Handle a local Tray request without contacting the Backend."""
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
            registration = self.registration.start()
            return {
                "ok": True,
                "type": REGISTRATION_START,
                "request_id": registration.request_id,
                "registration_code": registration.registration_code,
                "expires_at": registration.expires_at.isoformat(),
            }

        if message_type == REGISTRATION_CANCEL:
            self.registration.cancel()
            return {"ok": True, "type": REGISTRATION_CANCEL}

        return {"ok": False, "error": "unsupported_message_type"}
