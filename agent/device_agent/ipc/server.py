"""Minimal local IPC server for the Device Agent Service."""

from __future__ import annotations

import socket
import threading
from typing import Any

from .protocol import MAX_MESSAGE_SIZE, decode_message, encode_message


class IPCServer:
    """Small request/response IPC server used by the Device Agent."""

    def __init__(self) -> None:
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind(("127.0.0.1", 0))
        self._socket.listen(1)
        self._socket.settimeout(0.2)
        host, port = self._socket.getsockname()
        self.endpoint = f"tcp://{host}:{port}"
        self._running = False
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        """Start serving requests in a background thread."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._serve, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop the server and release its listening socket."""
        if not self._running:
            self._socket.close()
            return
        self._running = False
        if self._thread is not None:
            self._thread.join(timeout=1)
            self._thread = None
        self._socket.close()

    def _serve(self) -> None:
        while self._running:
            try:
                connection, _address = self._socket.accept()
            except socket.timeout:
                continue
            except OSError:
                break

            with connection:
                data = connection.recv(MAX_MESSAGE_SIZE)
                if not data:
                    continue
                try:
                    request = decode_message(data)
                    response = self._handle(request)
                    connection.sendall(encode_message(response))
                except (UnicodeDecodeError, ValueError, TypeError):
                    connection.sendall(encode_message({"ok": False}))

    @staticmethod
    def _handle(request: dict[str, Any]) -> dict[str, Any]:
        return {"ok": True, "type": request.get("type")}
