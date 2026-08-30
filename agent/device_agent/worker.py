import time

from .api import DeviceAgentAPI
from .auth import DeviceAuth
from .commands import CommandManager
from .config import POLL_INTERVAL_SECONDS
from .executor import CommandExecutor


class DeviceAgentWorker:
    def __init__(
        self,
        api: DeviceAgentAPI | None = None,
        executor: CommandExecutor | None = None,
    ):
        self.api = api or DeviceAgentAPI()
        self.auth = DeviceAuth(self.api)
        self.commands = CommandManager(self.api)
        self.executor = executor or CommandExecutor()

    def run_once(self):
        command = self.commands.claim_next()

        if command is None:
            return False

        command_id = command["id"]
        command_name = command["command"]
        payload = command.get("payload") or {}

        # Execute the command separately from reporting its result.
        # A completion/reporting failure must not be treated as an
        # execution failure.

        try:
            result = self.executor.execute(
                command_name,
                payload,
            )
        except Exception as exc:
            error_message = str(exc)

            try:
                self.commands.complete(
                    command_id=command_id,
                    status="failed",
                    error_message=error_message,
                )
            except Exception as complete_exc:
                print(
                    f"COMMAND COMPLETE FAILED: "
                    f"{command_id}: {complete_exc}"
                )

            print(
                f"COMMAND FAILED: {command_id} "
                f"{command_name}: {error_message}"
            )

            return True

        try:
            self.commands.complete(
                command_id=command_id,
                status="completed",
                result=result,
            )

            print(
                f"COMMAND COMPLETED: {command_id} "
                f"{command_name}"
            )

        except Exception as exc:
            print(
                f"COMMAND RESULT REPORT FAILED: "
                f"{command_id} {command_name}: {exc}"
            )

        return True

    def run(self):
        device_id = self.auth.authenticate()

        print(f"DEVICE AGENT STARTED: {device_id}")
        print(
            f"POLL INTERVAL: "
            f"{POLL_INTERVAL_SECONDS}s"
        )

        while True:
            try:
                self.run_once()
            except Exception as exc:
                print(f"WORKER ERROR: {exc}")

            time.sleep(POLL_INTERVAL_SECONDS)


def main():
    worker = DeviceAgentWorker()
    worker.run()


if __name__ == "__main__":
    main()
