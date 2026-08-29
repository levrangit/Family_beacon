from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

ALLOWED_WRITE_PATHS = (
    PROJECT_ROOT / "backend",
    PROJECT_ROOT / "supabase",
)

FORBIDDEN_PATHS = (
    PROJECT_ROOT / ".git",
    PROJECT_ROOT / ".env",
    PROJECT_ROOT / "agent" / ".env",
)

FORBIDDEN_COMMANDS = (
    "git push",
    "git reset --hard",
    "git clean -fd",
    "rm -rf",
)


def is_path_allowed(path: str | Path) -> bool:
    target = Path(path).resolve()

    if any(
        target == forbidden or forbidden in target.parents
        for forbidden in FORBIDDEN_PATHS
    ):
        return False

    return any(
        target == allowed or allowed in target.parents
        for allowed in ALLOWED_WRITE_PATHS
    )


def is_command_allowed(command: str) -> bool:
    normalized = command.strip().lower()

    return not any(
        forbidden in normalized
        for forbidden in FORBIDDEN_COMMANDS
    )


def validate_write_path(path: str | Path) -> None:
    if not is_path_allowed(path):
        raise PermissionError(
            f"Write operation is not allowed for path: {path}"
        )


def validate_command(command: str) -> None:
    if not is_command_allowed(command):
        raise PermissionError(
            f"Command is not allowed: {command}"
        )
