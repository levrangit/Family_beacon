from .commands import Command
from .executor import CommandExecutor


def main() -> None:
    executor = CommandExecutor()

    print("Family Beacon Windows Agent")
    print("Type 'ping', 'status' or 'exit'.")

    while True:
        try:
            command_name = input("agent> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if command_name == "exit":
            break

        if not command_name:
            continue

        try:
            command = Command.from_dict({"type": command_name})
            result = executor.execute(command)
            print(result)
        except ValueError as exc:
            print({
                "success": False,
                "error": str(exc),
            })

    print("Agent stopped.")


if __name__ == "__main__":
    main()
