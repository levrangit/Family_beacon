"""Windows Named Pipe IPC client for the Device Agent Tray."""

from __future__ import annotations

import os
from multiprocessing.connection import Client
from typing import Any

from .named_pipe_server import PIPE_PREFIX
from .protocol import MAX_MESSAGE_SIZE, decode_message, encode_message


class NamedPipeIPCClient:
    """Request/response client backed by a Windows Named Pipe."""

    requires_backend = False
    requires_supabase = False

    def __init__(self, endpoint: str = PIPE_PREFIX) -> None:
        self.endpoint = endpoint
        self._connection = None

    def connect(self) -> bool:
        """Connect to the local Device Agent Service Named Pipe."""
        if os.name != "nt":
            raise ConnectionError("Windows Named Pipes are available only on Windows")
        if not self.endpoint.startswith(PIPE_PREFIX):
            raise ConnectionError("Unsupported Named Pipe endpoint")

        try:
            self._connection = Client(self.endpoint, family="AF_PIPE")
        except (OSError, EOFError, ConnectionError) as exc:
            raise ConnectionError("Device Agent Service is unavailable") from exc
        return True

    def close(self) -> None:
        """Close the Named Pipe connection."""
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    def request(self, message: dict[str, Any]) -> dict[str, Any]:
        """Send one request and return one response."""
        if self._connection is None:
            raise ConnectionError("IPC client is not connected")

        try:
            self._connection.send_bytes(encode_message(message))
            data = self._connection.recv_bytes(MAX_MESSAGE_SIZE)
        except (OSError, EOFError, ConnectionError) as exc:
            raise ConnectionError("IPC request failed") from exc

        try:
            return decode_message(data)
        except (UnicodeDecodeError, ValueError, TypeError) as exc:
            raise ConnectionError("IPC service returned an invalid response") from exc
