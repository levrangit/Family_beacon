"""Shared message encoding and message types for Device Agent IPC."""

from __future__ import annotations

import json
from typing import Any

MAX_MESSAGE_SIZE = 64 * 1024
IPC_AUTHKEY = b"family-beacon-ipc-v1"

STATUS = "status"
REGISTRATION_START = "registration.start"
REGISTRATION_CANCEL = "registration.cancel"


def encode_message(message: dict[str, Any]) -> bytes:
    """Encode one IPC message as UTF-8 JSON terminated by a newline."""
    data = (json.dumps(message, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")
    if len(data) > MAX_MESSAGE_SIZE:
        raise ValueError("IPC message is too large")
    return data


def decode_message(data: bytes) -> dict[str, Any]:
    """Decode one UTF-8 JSON IPC message."""
    if len(data) > MAX_MESSAGE_SIZE:
        raise ValueError("IPC message is too large")
    message = json.loads(data.decode("utf-8"))
    if not isinstance(message, dict):
        raise ValueError("IPC message must be a JSON object")
    return message
