"""Minimal IPC client used by the Device Agent Tray."""

from __future__ import annotations

import json
import socket
from typing import Any


class IPCClient:
    """Request/response client for the local Device Agent IPC service."""

    requires_backend = False
    requires_supabase = False

    def __init__(self, endpoint: str) -> None:
        self.endpoint = endpoint
        self._socket: socket.socket | None = None

    def connect(self) -> bool:
        if not self.endpoint.startswith("tcp://"):
            raise ConnectionError("Unsupported IPC endpoint")

        try:
            address = self.endpoint.removeprefix("tcp://")
            host, port_text = address.rsplit(":", 1)
            self._socket = socket.create_connection((host, int(port_text)), timeout=1)
        except (OSError, ValueError) as exc:
            raise ConnectionError("Device Agent Service is unavailable") from exc
        return True

    def request(self, message: dict[str, Any]) -> dict[str, Any]:
        if self._socket is None:
            raise ConnectionError("IPC client is not connected")

        try:
            self._socket.sendall(json.dumps(message).encode("utf-8"))
            data = self._socket.recv(64 * 1024)
        except OSError as exc:
            raise ConnectionError("IPC request failed") from exc

        if not data:
            raise ConnectionError("IPC service closed the connection")
        return json.loads(data.decode("utf-8"))
