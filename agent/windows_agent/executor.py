import platform
import socket
from datetime import datetime, timezone

from .commands import Command, CommandType


class CommandExecutor:
    def execute(self, command: Command) -> dict:
        if command.type == CommandType.PING:
            return {
                "success": True,
                "command": command.type.value,
                "message": "pong",
            }

        if command.type == CommandType.STATUS:
            return self._status()

        if command.type in {
            CommandType.LOCK,
            CommandType.SHUTDOWN,
            CommandType.RESTART,
        }:
            return {
                "success": False,
                "command": command.type.value,
                "status": "not_implemented",
                "message": "Command execution is not implemented yet",
            }

        return {
            "success": False,
            "command": command.type.value,
            "status": "unsupported",
            "message": "Unsupported command",
        }

    def _status(self) -> dict:
        return {
            "success": True,
            "command": CommandType.STATUS.value,
            "status": "online",
            "hostname": socket.gethostname(),
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
