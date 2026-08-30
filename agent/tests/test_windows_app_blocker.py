import pytest

from device_agent.windows_app_blocker import WindowsAppBlocker


def test_blocker_rejects_non_windows(monkeypatch):
    monkeypatch.setattr(
        "device_agent.windows_app_blocker.platform.system",
        lambda: "Linux",
    )

    blocker = WindowsAppBlocker()

    with pytest.raises(
        RuntimeError,
        match="supported only on Windows",
    ):
        blocker.block("notepad.exe")


def test_blocker_requires_app():
    blocker = WindowsAppBlocker()

    with pytest.raises(
        ValueError,
        match="app",
    ):
        blocker.block("")


def test_blocker_normalizes_application_name(monkeypatch):
    monkeypatch.setattr(
        "device_agent.windows_app_blocker.platform.system",
        lambda: "Windows",
    )

    blocker = WindowsAppBlocker()

    monkeypatch.setattr(
        blocker,
        "_apply_block_rule",
        lambda app: None,
    )

    result = blocker.block("notepad.exe")

    assert result == {
        "status": "app_blocked",
        "app": "notepad.exe",
    }


def test_blocker_calls_windows_rule(monkeypatch):
    monkeypatch.setattr(
        "device_agent.windows_app_blocker.platform.system",
        lambda: "Windows",
    )

    calls = []

    blocker = WindowsAppBlocker()

    monkeypatch.setattr(
        blocker,
        "_apply_block_rule",
        lambda app: calls.append(app),
    )

    result = blocker.block("C:\\Windows\\System32\\notepad.exe")

    assert calls == [
        "C:\\Windows\\System32\\notepad.exe",
    ]

    assert result == {
        "status": "app_blocked",
        "app": "C:\\Windows\\System32\\notepad.exe",
    }
