"""Windows Named Pipe IPC client for the Device Agent Tray."""

from __future__ import annotations

import ctypes
import os
from typing import Any

from .named_pipe_server import PIPE_PREFIX
from .protocol import MAX_MESSAGE_SIZE, decode_message, encode_message

if os.name == "nt":
    from ctypes import wintypes

    _kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    _GENERIC_READ = 0x80000000
    _GENERIC_WRITE = 0x40000000
    _OPEN_EXISTING = 3
    _FILE_ATTRIBUTE_NORMAL = 0x00000080
    _ERROR_FILE_NOT_FOUND = 2
    _ERROR_PATH_NOT_FOUND = 3
    _ERROR_PIPE_BUSY = 231

    _kernel32.CreateFileW.argtypes = [
        wintypes.LPCWSTR,
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.LPVOID,
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.HANDLE,
    ]
    _kernel32.CreateFileW.restype = wintypes.HANDLE
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


class NamedPipeIPCClient:
    """Request/response client backed by a Windows Named Pipe."""

    requires_backend = False
    requires_supabase = False

    def __init__(self, endpoint: str = PIPE_PREFIX) -> None:
        self.endpoint = endpoint
        self._handle = None

    def connect(self) -> bool:
        """Connect to the local Device Agent Service Named Pipe."""
        if os.name != "nt":
            raise ConnectionError("Windows Named Pipes are available only on Windows")
        if not self.endpoint.startswith(r"\\.\pipe\family-beacon"):
            raise ConnectionError("Unsupported Named Pipe endpoint")

        handle = _kernel32.CreateFileW(
            self.endpoint,
            _GENERIC_READ | _GENERIC_WRITE,
            0,
            None,
            _OPEN_EXISTING,
            _FILE_ATTRIBUTE_NORMAL,
            None,
        )
        if handle == wintypes.HANDLE(-1).value:
            error = ctypes.get_last_error()
            if error in {_ERROR_FILE_NOT_FOUND, _ERROR_PATH_NOT_FOUND, _ERROR_PIPE_BUSY}:
                raise ConnectionError("Device Agent Service is unavailable")
            raise ConnectionError("Unable to connect to Device Agent Service")

        self._handle = handle
        return True

    def close(self) -> None:
        """Close the Named Pipe connection."""
        if self._handle is not None:
            _kernel32.CloseHandle(self._handle)
            self._handle = None

    def request(self, message: dict[str, Any]) -> dict[str, Any]:
        """Send one request and return one response."""
        if self._handle is None:
            raise ConnectionError("IPC client is not connected")

        encoded = encode_message(message)
        written = wintypes.DWORD()
        if not _kernel32.WriteFile(
            self._handle,
            encoded,
            len(encoded),
            ctypes.byref(written),
            None,
        ):
            raise ConnectionError("IPC request failed")

        buffer = ctypes.create_string_buffer(MAX_MESSAGE_SIZE)
        read = wintypes.DWORD()
        if not _kernel32.ReadFile(
            self._handle,
            buffer,
            MAX_MESSAGE_SIZE,
            ctypes.byref(read),
            None,
        ):
            raise ConnectionError("IPC service returned no response")

        try:
            return decode_message(buffer.raw[: read.value])
        except (UnicodeDecodeError, ValueError, TypeError) as exc:
            raise ConnectionError("IPC service returned an invalid response") from exc
