"""Windows Named Pipe IPC server for the Device Agent Service."""

from __future__ import annotations

import ctypes
import threading
from typing import Any

from .protocol import MAX_MESSAGE_SIZE, decode_message, encode_message


PIPE_PREFIX = r"\\.\pipe\family-beacon"

if __import__("os").name == "nt":
    from ctypes import wintypes

    _kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    _INVALID_HANDLE_VALUE = wintypes.HANDLE(-1).value
    _PIPE_ACCESS_DUPLEX = 0x00000003
    _PIPE_TYPE_MESSAGE = 0x00000004
    _PIPE_READMODE_MESSAGE = 0x00000002
    _PIPE_WAIT = 0x00000000
    _PIPE_UNLIMITED_INSTANCES = 255
    _ERROR_PIPE_CONNECTED = 535
    _ERROR_BROKEN_PIPE = 109

    _kernel32.CreateNamedPipeW.argtypes = [
        wintypes.LPCWSTR,
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.LPVOID,
    ]
    _kernel32.CreateNamedPipeW.restype = wintypes.HANDLE
    _kernel32.ConnectNamedPipe.argtypes = [wintypes.HANDLE, wintypes.LPVOID]
    _kernel32.ConnectNamedPipe.restype = wintypes.BOOL
    _kernel32.DisconnectNamedPipe.argtypes = [wintypes.HANDLE]
    _kernel32.DisconnectNamedPipe.restype = wintypes.BOOL
    _kernel32.ReadFile.argtypes = [
        wintypes.HANDLE,
        wintypes.LPVOID,
        wintypes.DWORD,
        ctypes.POINTER(wintypes.DWORD),
        wintypes.LPVOID,
    ]
    _kernel32.ReadFile.restype = wintypes.BOOL
    _kernel32.WriteFile.argtypes = [
        wintypes.HANDLE,
        wintypes.LPCVOID,
        wintypes.DWORD,
        ctypes.POINTER(wintypes.DWORD),
        wintypes.LPVOID,
    ]
    _kernel32.WriteFile.restype = wintypes.BOOL
    _kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    _kernel32.CloseHandle.restype = wintypes.BOOL


class NamedPipeIPCServer:
    """Small request/response server backed by a Windows Named Pipe."""

    def __init__(self) -> None:
        if __import__("os").name != "nt":
            raise OSError("Windows Named Pipes are available only on Windows")
        self.endpoint = PIPE_PREFIX
        self._running = False
        self._thread: threading.Thread | None = None
        self._handle = None

    def start(self) -> None:
        """Start accepting one Named Pipe client in a background thread."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._serve, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop the server and release the Named Pipe handle."""
        self._running = False
        if self._handle is not None:
            _kernel32.CloseHandle(self._handle)
            self._handle = None
        if self._thread is not None:
            self._thread.join(timeout=1)
            self._thread = None

    def _serve(self) -> None:
        while self._running:
            handle = _kernel32.CreateNamedPipeW(
                self.endpoint,
                _PIPE_ACCESS_DUPLEX,
                _PIPE_TYPE_MESSAGE | _PIPE_READMODE_MESSAGE | _PIPE_WAIT,
                _PIPE_UNLIMITED_INSTANCES,
                MAX_MESSAGE_SIZE,
                MAX_MESSAGE_SIZE,
                0,
                None,
            )
            if handle == _INVALID_HANDLE_VALUE:
                return
            self._handle = handle

            connected = _kernel32.ConnectNamedPipe(handle, None)
            if not connected and ctypes.get_last_error() != _ERROR_PIPE_CONNECTED:
                _kernel32.CloseHandle(handle)
                self._handle = None
                if not self._running:
                    return
                continue

            try:
                self._serve_connection(handle)
            finally:
                _kernel32.DisconnectNamedPipe(handle)
                _kernel32.CloseHandle(handle)
                self._handle = None

    @staticmethod
    def _serve_connection(handle: Any) -> None:
        buffer = ctypes.create_string_buffer(MAX_MESSAGE_SIZE)
        read = wintypes.DWORD()
        if not _kernel32.ReadFile(handle, buffer, MAX_MESSAGE_SIZE, ctypes.byref(read), None):
            if ctypes.get_last_error() != _ERROR_BROKEN_PIPE:
                return
            return

        data = buffer.raw[: read.value]
        try:
            request = decode_message(data)
            response = {"ok": True, "type": request.get("type")}
        except (UnicodeDecodeError, ValueError, TypeError):
            response = {"ok": False}

        encoded = encode_message(response)
        written = wintypes.DWORD()
        _kernel32.WriteFile(handle, encoded, len(encoded), ctypes.byref(written), None)
