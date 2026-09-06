"""Shared message encoding for Device Agent IPC."""

from __future__ import annotations

import json
from typing import Any

MAX_MESSAGE_SIZE = 64 * 1024


def encode_message(message: dict[str, Any]) -> bytes:
    """Encode one IPC message as UTF-8 JSON terminated by a newline."""
    return (json.dumps(message, separators=(",", ":")) + "\n").encode("utf-8")


def decode_message(data: bytes) -> dict[str, Any]:
    """Decode one UTF-8 JSON IPC message."""
    message = json.loads(data.decode("utf-8"))
    if not isinstance(message, dict):
        raise ValueError("IPC message must be a JSON object")
    return message
