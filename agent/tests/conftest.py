"""Pytest configuration for the Windows-only Device Agent test contour."""

import os
import sys
from pathlib import Path

import pytest


IS_WINDOWS = sys.platform == "win32"
IS_CODESPACES = os.getenv("CODESPACES", "").lower() == "true"


pytestmark = pytest.mark.windows


def pytest_ignore_collect(collection_path: Path, config):
    """Prevent Linux from importing Windows-only Agent test modules."""

    if IS_WINDOWS:
        return None
    if collection_path.name == "conftest.py":
        return None
    if collection_path.suffix == ".py" and collection_path.parent.name == "tests":
        return True
    return None
