import pytest

from device_agent.executor import CommandExecutor


def test_shutdown_is_supported():
    assert "shutdown" in CommandExecutor.SUPPORTED_COMMANDS


def test_shutdown_rejected_on_non_windows(monkeypatch):
    monkeypatch.setattr(
        "device_agent.executor.platform.system",
        lambda: "Linux",
    )

    executor = CommandExecutor()

    with pytest.raises(
        RuntimeError,
        match="supported only on Windows",
    ):
        executor.execute("shutdown")


def test_shutdown_calls_windows_shutdown(monkeypatch):
    monkeypatch.setattr(
        "device_agent.executor.platform.system",
        lambda: "Windows",
    )

    calls = []

    class FakeSubprocess:
        @staticmethod
        def run(command, check):
            calls.append(
                {
                    "command": command,
                    "check": check,
                }
            )

    monkeypatch.setattr(
        "device_agent.executor.subprocess",
        FakeSubprocess,
        raising=False,
    )

    executor = CommandExecutor()

    result = executor.execute("shutdown")

    assert calls == [
        {
            "command": [
                "shutdown",
                "/s",
                "/t",
                "0",
            ],
            "check": True,
        }
    ]

    assert result == {
        "status": "shutdown",
    }


def test_shutdown_reports_windows_failure(monkeypatch):
    monkeypatch.setattr(
        "device_agent.executor.platform.system",
        lambda: "Windows",
    )

    class FakeSubprocess:
        @staticmethod
        def run(command, check):
            raise RuntimeError("shutdown failed")

    monkeypatch.setattr(
        "device_agent.executor.subprocess",
        FakeSubprocess,
        raising=False,
    )

    executor = CommandExecutor()

    with pytest.raises(
        RuntimeError,
        match="shutdown failed",
    ):
        executor.execute("shutdown")
