"""Windows Named Pipe IPC server for the Device Agent Service."""

from __future__ import annotations

import os
import threading
from multiprocessing.connection import Client, Listener
from typing import Any, Callable

from .protocol import IPC_AUTHKEY, MAX_MESSAGE_SIZE, decode_message, encode_message


PIPE_ENDPOINT = r"\\.\pipe\family-beacon"
PIPE_PREFIX = PIPE_ENDPOINT


class NamedPipeIPCServer:
    """Request/response server backed by a stable Windows Named Pipe."""

    def __init__(self, handler: Callable[[dict[str, Any]], dict[str, Any]] | None = None) -> None:
        if os.name != "nt":
            raise OSError("Windows Named Pipes are available only on Windows")
        self.endpoint = PIPE_ENDPOINT
        self._handler = handler or self._default_handler
        self._listener = Listener(self.endpoint, family="AF_PIPE", authkey=IPC_AUTHKEY)
        self._running = False
        self._thread: threading.Thread | None = None
        self._connection: Any | None = None

    def start(self) -> None:
        """Start accepting Named Pipe clients in a background thread."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._serve, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop the Named Pipe listener and active connection."""
        if not self._running:
            self._listener.close()
            return
        self._running = False
        connection = self._connection
        self._connection = None
        if connection is not None:
            try:
                connection.close()
            except (OSError, EOFError):
                pass
        try:
            wake_connection = Client(self.endpoint, family="AF_PIPE", authkey=IPC_AUTHKEY)
        except (OSError, EOFError, ConnectionError):
            wake_connection = None
        if wake_connection is not None:
            wake_connection.close()
        self._listener.close()
        if self._thread is not None:
            self._thread.join(timeout=1)
            if not self._thread.is_alive():
                self._thread = None

    def _serve(self) -> None:
        while self._running:
            try:
                connection = self._listener.accept()
            except (OSError, EOFError):
                break
            self._connection = connection
            try:
                self._serve_connection(connection)
            finally:
                self._connection = None
                connection.close()

    def _serve_connection(self, connection: Any) -> None:
        """Serve requests until the client closes the connection."""
        while self._running:
            response = self._read_request(connection)
            if response is None:
                break
            self._send_response(connection, response)

    def _read_request(self, connection: Any) -> dict[str, Any] | None:
        try:
            data = connection.recv_bytes(MAX_MESSAGE_SIZE)
        except (EOFError, OSError):
            return None

        try:
            request = decode_message(data)
            return self._handler(request)
        except (UnicodeDecodeError, ValueError, TypeError) as exc:
            return {"ok": False, "error": str(exc)}

    @staticmethod
    def _send_response(connection: Any, response: dict[str, Any]) -> None:
        try:
            connection.send_bytes(encode_message(response))
        except (BrokenPipeError, EOFError, OSError):
            return

    @staticmethod
    def _default_handler(request: dict[str, Any]) -> dict[str, Any]:
        return {"ok": True, "type": request.get("type")}
