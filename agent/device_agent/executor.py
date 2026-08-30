import ctypes
import getpass
import platform
import subprocess


class CommandExecutor:
    SUPPORTED_COMMANDS = {
        "get_status",
        "lock",
        "shutdown",
        "restart",
        "sleep",
        "get_device_state",
        "set_time_limit",
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

        if command == "sleep":
            return self._sleep()

        if command == "get_device_state":
            return self._get_device_state()

        if command == "set_time_limit":
            return self._set_time_limit(payload)

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

    @staticmethod
    def _sleep() -> dict:
        if platform.system() != "Windows":
            raise RuntimeError(
                "Sleep command is supported only on Windows"
            )

        subprocess.run(
            [
                "rundll32.exe",
                "powrprof.dll,SetSuspendState",
                "0",
                "1",
                "0",
            ],
            check=True,
        )

        return {
            "status": "sleeping",
        }


    @staticmethod
    def _get_device_state() -> dict:
        if platform.system() != "Windows":
            raise RuntimeError(
                "Get device state command is supported only on Windows"
            )

        return {
            "status": "online",
            "platform": platform.system(),
            "hostname": platform.node(),
            "username": getpass.getuser(),
        }

    @staticmethod
    def _set_time_limit(payload: dict) -> dict:
        if "minutes" not in payload:
            raise ValueError(
                "minutes is required"
            )

        minutes = payload["minutes"]

        if isinstance(minutes, bool) or not isinstance(minutes, int):
            raise ValueError(
                "minutes must be an integer"
            )

        if minutes <= 0:
            raise ValueError(
                "minutes must be positive"
            )

        if platform.system() != "Windows":
            raise RuntimeError(
                "Set time limit command is supported only on Windows"
            )

        return {
            "status": "time_limit_set",
            "minutes": minutes,
        }
