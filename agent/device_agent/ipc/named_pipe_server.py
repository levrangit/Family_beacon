"""Windows Named Pipe IPC server for the Device Agent Service."""

from __future__ import annotations

import os
import threading
import uuid
from multiprocessing.connection import Listener
from typing import Any

from .protocol import MAX_MESSAGE_SIZE, decode_message, encode_message


PIPE_PREFIX = r"\\.\pipe\family-beacon"


class NamedPipeIPCServer:
    """Small request/response server backed by a Windows Named Pipe."""

    def __init__(self) -> None:
        if os.name != "nt":
            raise OSError("Windows Named Pipes are available only on Windows")
        self.endpoint = f"{PIPE_PREFIX}-{uuid.uuid4().hex}"
        self._listener = Listener(self.endpoint, family="AF_PIPE")
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
        """Stop the server and release the Named Pipe listener."""
        if not self._running:
            try:
                self._listener.close()
            except OSError:
                pass
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

    @staticmethod
    def _serve_connection(connection: Any) -> None:
        try:
            data = connection.recv_bytes(MAX_MESSAGE_SIZE)
            request = decode_message(data)
            response = {"ok": True, "type": request.get("type")}
        except (EOFError, OSError, UnicodeDecodeError, ValueError, TypeError):
            response = {"ok": False}

        try:
            connection.send_bytes(encode_message(response))
        except (BrokenPipeError, EOFError, OSError):
            pass
