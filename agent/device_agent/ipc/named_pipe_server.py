"""Windows Named Pipe IPC server for the Device Agent Service."""

from __future__ import annotations

import os
import threading
from multiprocessing.connection import Listener
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

    def start(self) -> None:
        """Start accepting Named Pipe clients in a background thread."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._serve, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop the Named Pipe listener."""
        if not self._running:
            self._listener.close()
            return
        self._running = False
        self._listener.close()
        if self._thread is not None:
            self._thread.join(timeout=1)
            self._thread = None

    def _serve(self) -> None:
        while self._running:
            try:
                connection = self._listener.accept()
            except (OSError, EOFError):
                break
            try:
                self._serve_connection(connection)
            finally:
                connection.close()

    def _serve_connection(self, connection: Any) -> None:
        response = self._read_request(connection)
        self._send_response(connection, response)

    def _read_request(self, connection: Any) -> dict[str, Any]:
        try:
            data = connection.recv_bytes(MAX_MESSAGE_SIZE)
            request = decode_message(data)
            return self._handler(request)
        except (EOFError, OSError, UnicodeDecodeError, ValueError, TypeError) as exc:
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
