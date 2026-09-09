"""Pytest configuration for the Windows-only Device Agent test contour."""

import os
import sys

import pytest


IS_WINDOWS = sys.platform == "win32"
IS_CODESPACES = os.getenv("CODESPACES", "").lower() == "true"


# The Device Agent is currently supported only on Windows.  Mark the whole
# Agent test contour explicitly so Linux/Codespaces does not pretend to test
# Windows-specific production behavior.
pytestmark = pytest.mark.windows


def pytest_collection_modifyitems(config, items):
    """Skip Windows Agent tests when pytest is running outside Windows."""

    if IS_WINDOWS:
        return

    reason = "Family Beacon Device Agent tests are Windows-only"
    if IS_CODESPACES:
        reason += " (GitHub Codespaces/Linux)"

    skip = pytest.mark.skip(reason=reason)
    for item in items:
        item.add_marker(skip)
