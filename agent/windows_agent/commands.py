from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class CommandType(StrEnum):
    PING = "ping"
    STATUS = "status"
    LOCK = "lock"
    SHUTDOWN = "shutdown"
    RESTART = "restart"


@dataclass(frozen=True)
class Command:
    type: CommandType
    request_id: str | None = None
    parameters: dict[str, Any] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Command":
        command_type = data.get("type")

        if not isinstance(command_type, str):
            raise ValueError("Command type is required")

        try:
            command = CommandType(command_type)
        except ValueError as exc:
            raise ValueError(
                f"Unsupported command type: {command_type}"
            ) from exc

        return cls(
            type=command,
            request_id=data.get("request_id"),
            parameters=data.get("parameters"),
        )
