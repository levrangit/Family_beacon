from pathlib import Path

from guardrails.rules import validate_write_path


def write_file(path: str | Path, content: str) -> Path:
    target = Path(path).resolve()

    validate_write_path(target)

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")

    return target


def read_file(path: str | Path) -> str:
    target = Path(path).resolve()

    return target.read_text(encoding="utf-8")
