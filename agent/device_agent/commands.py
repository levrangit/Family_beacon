from .api import DeviceAgentAPI


class CommandManager:
    def __init__(self, api: DeviceAgentAPI):
        self.api = api

    def claim_next(self):
        return self.api.claim_command()

    def complete(
        self,
        command_id: str,
        status: str,
        result: dict | None = None,
        error_message: str | None = None,
    ):
        return self.api.complete_command(
            command_id=command_id,
            status=status,
            result=result,
            error_message=error_message,
        )
