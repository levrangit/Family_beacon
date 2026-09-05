from __future__ import annotations

from pathlib import Path


_VERSION_FILE = Path(__file__).resolve().parents[1] / "VERSION"


def get_project_version() -> str:
    """Return the project version from the root VERSION file."""
    return _VERSION_FILE.read_text(encoding="utf-8").strip()
