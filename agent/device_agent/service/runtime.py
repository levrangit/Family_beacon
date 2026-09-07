"""Runtime lifecycle for the Family Beacon Device Agent Windows Service."""

from __future__ import annotations

import threading

from ..config import load_config
from ..identity import collect_identity
from ..logging import setup_logging


class AgentRuntime:
    """Own the Device Agent service runtime independently of Windows SCM.

    The runtime contains application lifecycle logic. The Windows-specific
    ServiceFramework adapter lives in ``service.py``.
    """

    def __init__(self) -> None:
        self.config = load_config()
        self.logger = setup_logging(self.config.log_level)
        self._stop_event = threading.Event()

    def start(self) -> None:
        """Start the runtime and its currently implemented services."""
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

    def run(self) -> None:
        """Keep the runtime alive until a stop request is received."""
        self.start()
        self._stop_event.wait()
        self.stop()

    def request_stop(self) -> None:
        """Request graceful runtime shutdown."""
        self._stop_event.set()

    def stop(self) -> None:
        """Stop the runtime and release currently owned resources."""
        if not self._stop_event.is_set():
            self._stop_event.set()

        self.logger.info(
            "Device Agent runtime %s stopped",
            self.config.agent_version,
        )
