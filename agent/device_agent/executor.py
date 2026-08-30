class CommandExecutor:
    SUPPORTED_COMMANDS = {
        "get_status",
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

        raise ValueError(
            f"Unsupported device command: {command}"
        )

    @staticmethod
    def _get_status() -> dict:
        return {
            "status": "online",
        }
