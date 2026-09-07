"""TDD tests for Device Agent Tray integration."""

from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from agent.device_agent.tray.tray import DeviceAgentTray


def _app() -> QApplication:
    return QApplication.instance() or QApplication([])


class FakeNamedPipeIPCClient:
    """Small in-process Service stand-in for Tray UI tests."""

    def __init__(self) -> None:
        self.requests: list[dict[str, str]] = []
        self.closed = False

    def connect(self) -> bool:
        return True

    def close(self) -> None:
        self.closed = True

    def request(self, message: dict[str, str]) -> dict[str, object]:
        self.requests.append(message)
        if message["type"] == "registration.start":
            return {
                "ok": True,
                "type": "registration.start",
                "request_id": "test-request",
                "registration_code": "ABC234",
                "expires_at": "2030-01-01T00:10:00+00:00",
            }
        return {"ok": True, "type": message["type"]}


def test_tray_opens_pairing_window_from_service_registration(monkeypatch) -> None:
    monkeypatch.setattr(
        "agent.device_agent.tray.tray.NamedPipeIPCClient",
        FakeNamedPipeIPCClient,
    )
    tray = DeviceAgentTray(_app())

    tray._registration_placeholder()
    _app().processEvents()

    assert tray._pairing_window is not None
    assert tray._pairing_window.isVisible()
    assert tray._pairing_window.pairing_code == "ABC234"

    tray._pairing_window.close()


def test_tray_reuses_existing_pairing_window_on_repeated_registration(monkeypatch) -> None:
    monkeypatch.setattr(
        "agent.device_agent.tray.tray.NamedPipeIPCClient",
        FakeNamedPipeIPCClient,
    )
    tray = DeviceAgentTray(_app())

    tray._registration_placeholder()
    first_window = tray._pairing_window

    tray._registration_placeholder()
    _app().processEvents()

    assert tray._pairing_window is first_window

    tray._pairing_window.close()


def test_tray_releases_pairing_window_reference_after_window_is_closed(monkeypatch) -> None:
    monkeypatch.setattr(
        "agent.device_agent.tray.tray.NamedPipeIPCClient",
        FakeNamedPipeIPCClient,
    )
    tray = DeviceAgentTray(_app())

    tray._registration_placeholder()
    window = tray._pairing_window

    window.close()
    _app().processEvents()

    assert tray._pairing_window is None


def test_tray_can_open_pairing_window_again_after_previous_window_is_closed(monkeypatch) -> None:
    monkeypatch.setattr(
        "agent.device_agent.tray.tray.NamedPipeIPCClient",
        FakeNamedPipeIPCClient,
    )
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
