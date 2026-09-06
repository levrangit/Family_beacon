"""Minimal IPC client used by the Device Agent Tray."""

from __future__ import annotations

import socket
from typing import Any

from ..ipc.protocol import MAX_MESSAGE_SIZE, decode_message, encode_message


class IPCClient:
    """Request/response client for the local Device Agent IPC service."""

    requires_backend = False
    requires_supabase = False

    def __init__(self, endpoint: str) -> None:
        self.endpoint = endpoint
        self._socket: socket.socket | None = None

    def connect(self) -> bool:
        """Connect to the local IPC service."""
        if not self.endpoint.startswith("tcp://"):
            raise ConnectionError("Unsupported IPC endpoint")

        try:
            host, port_text = self.endpoint.removeprefix("tcp://").rsplit(":", 1)
            self._socket = socket.create_connection((host, int(port_text)), timeout=1)
        except (OSError, ValueError) as exc:
            raise ConnectionError("Device Agent Service is unavailable") from exc
        return True

    def close(self) -> None:
        """Close the IPC connection when it is no longer needed."""
        if self._socket is not None:
            self._socket.close()
            self._socket = None

    def request(self, message: dict[str, Any]) -> dict[str, Any]:
        """Send one request and return one response."""
        if self._socket is None:
            raise ConnectionError("IPC client is not connected")

        try:
            self._socket.sendall(encode_message(message))
            data = self._socket.recv(MAX_MESSAGE_SIZE)
        except OSError as exc:
            raise ConnectionError("IPC request failed") from exc

        if not data:
            raise ConnectionError("IPC service closed the connection")
        try:
            return decode_message(data)
        except (UnicodeDecodeError, ValueError, TypeError) as exc:
            raise ConnectionError("IPC service returned an invalid response") from exc
