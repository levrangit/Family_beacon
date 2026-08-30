import ctypes
import platform
import subprocess


class CommandExecutor:
    SUPPORTED_COMMANDS = {
        "get_status",
        "lock",
        "shutdown",
        "restart",
    }

    def execute(
        self,
        command: str,
        payload: dict | None = None,
    ) -> dict:
        payload = payload or {}

        if command not in self.SUPPORTED_COMMANDS:
            raise ValueError(
                f"Unsupported device command: {command}"
            )

        if command == "get_status":
            return self._get_status()

        if command == "lock":
            return self._lock()

        if command == "shutdown":
            return self._shutdown()

        if command == "restart":
            return self._restart()

        raise ValueError(
            f"Unsupported device command: {command}"
        )

    @staticmethod
    def _get_status() -> dict:
        return {
            "status": "online",
        }

    @staticmethod
    def _lock() -> dict:
        if platform.system() != "Windows":
            raise RuntimeError(
                "Lock command is supported only on Windows"
            )

        result = ctypes.windll.user32.LockWorkStation()

        if result == 0:
            raise RuntimeError(
                "Windows failed to lock the workstation"
            )

        return {
            "status": "locked",
        }

    @staticmethod
    def _shutdown() -> dict:
        if platform.system() != "Windows":
            raise RuntimeError(
                "Shutdown command is supported only on Windows"
            )

        subprocess.run(
            ["shutdown", "/s", "/t", "0"],
            check=True,
        )

        return {
            "status": "shutdown",
        }

    @staticmethod
    def _restart() -> dict:
        if platform.system() != "Windows":
            raise RuntimeError(
                "Restart command is supported only on Windows"
            )

        subprocess.run(
            ["shutdown", "/r", "/t", "0"],
            check=True,
        )

        return {
            "status": "restarting",
        }
