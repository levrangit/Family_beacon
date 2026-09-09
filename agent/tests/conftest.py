"""Pytest configuration for the Windows-only Device Agent test contour."""

import os
import sys
from pathlib import Path

import pytest
from _pytest.nodes import Collector


IS_WINDOWS = sys.platform == "win32"
IS_CODESPACES = os.getenv("CODESPACES", "").lower() == "true"


pytestmark = pytest.mark.windows


class WindowsOnlySkipItem(pytest.Item):
    """A collection-safe skipped item for Windows-only Agent test files."""

    def runtest(self) -> None:
        reason = "Device Agent tests are Windows-only — запуск только на Windows"
        if IS_CODESPACES:
            reason += " (GitHub Codespaces/Linux)"
        pytest.skip(reason)

    def reportinfo(self):
        return self.path, 0, self.name


class WindowsOnlySkipFile(Collector):
    """Collect a single skipped item without importing the test module."""

    def collect(self):
        yield WindowsOnlySkipItem.from_parent(self, name=self.path.name)


def pytest_collect_file(file_path: Path, parent: Collector):
    """Skip the Agent test file before Linux can import Windows-only modules."""

    if IS_WINDOWS or file_path.name == "conftest.py":
        return None
    if file_path.suffix == ".py" and file_path.parent.name == "tests":
        return WindowsOnlySkipFile.from_parent(
            parent,
            path=file_path,
            name=file_path.name,
        )
    return None
