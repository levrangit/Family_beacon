"""TDD tests for Device Agent Tray integration."""

from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from agent.device_agent.tray.tray import DeviceAgentTray


def _app() -> QApplication:
    return QApplication.instance() or QApplication([])


def test_tray_opens_pairing_window_when_registration_is_requested() -> None:
    tray = DeviceAgentTray(_app())

    tray._registration_placeholder()
    _app().processEvents()

    assert tray._pairing_window is not None
    assert tray._pairing_window.isVisible()

    tray._pairing_window.close()


def test_tray_reuses_existing_pairing_window_on_repeated_registration() -> None:
    tray = DeviceAgentTray(_app())

    tray._registration_placeholder()
    first_window = tray._pairing_window

    tray._registration_placeholder()
    _app().processEvents()

    assert tray._pairing_window is first_window

    tray._pairing_window.close()


def test_tray_releases_pairing_window_reference_after_window_is_closed() -> None:
    tray = DeviceAgentTray(_app())

    tray._registration_placeholder()
    window = tray._pairing_window

    window.close()
    _app().processEvents()

    assert tray._pairing_window is None


def test_tray_can_open_pairing_window_again_after_previous_window_is_closed() -> None:
    tray = DeviceAgentTray(_app())

    tray._registration_placeholder()
    first_window = tray._pairing_window
    first_window.close()
    _app().processEvents()

    tray._registration_placeholder()
    _app().processEvents()

    assert tray._pairing_window is not None
    assert tray._pairing_window is not first_window

    tray._pairing_window.close()
