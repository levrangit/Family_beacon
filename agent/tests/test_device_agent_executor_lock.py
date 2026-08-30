import pytest

from device_agent.executor import CommandExecutor


def test_lock_is_supported():
    assert "lock" in CommandExecutor.SUPPORTED_COMMANDS


def test_lock_rejected_on_non_windows(monkeypatch):
    monkeypatch.setattr(
        "device_agent.executor.platform.system",
        lambda: "Linux",
    )

    executor = CommandExecutor()

    with pytest.raises(
        RuntimeError,
        match="supported only on Windows",
    ):
        executor.execute("lock")


def test_lock_calls_windows_lock_workstation(monkeypatch):
    monkeypatch.setattr(
        "device_agent.executor.platform.system",
        lambda: "Windows",
    )

    calls = []

    class FakeUser32:
        @staticmethod
        def LockWorkStation():
            calls.append("LockWorkStation")
            return 1

    class FakeWindll:
        user32 = FakeUser32()

    monkeypatch.setattr(
        "device_agent.executor.ctypes.windll",
        FakeWindll(),
        raising=False,
    )

    executor = CommandExecutor()

    result = executor.execute("lock")

    assert calls == ["LockWorkStation"]
    assert result == {
        "status": "locked",
    }


def test_lock_reports_windows_failure(monkeypatch):
    monkeypatch.setattr(
        "device_agent.executor.platform.system",
        lambda: "Windows",
    )

    class FakeUser32:
        @staticmethod
        def LockWorkStation():
            return 0

    class FakeWindll:
        user32 = FakeUser32()

    monkeypatch.setattr(
        "device_agent.executor.ctypes.windll",
        FakeWindll(),
        raising=False,
    )

    executor = CommandExecutor()

    with pytest.raises(
        RuntimeError,
        match="failed to lock",
    ):
        executor.execute("lock")
