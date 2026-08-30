import pytest

from device_agent.executor import CommandExecutor


def test_restart_is_supported():
    assert "restart" in CommandExecutor.SUPPORTED_COMMANDS


def test_restart_rejected_on_non_windows(monkeypatch):
    monkeypatch.setattr(
        "device_agent.executor.platform.system",
        lambda: "Linux",
    )

    executor = CommandExecutor()

    with pytest.raises(
        RuntimeError,
        match="supported only on Windows",
    ):
        executor.execute("restart")


def test_restart_calls_windows_restart(monkeypatch):
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

    result = executor.execute("restart")

    assert calls == [
        {
            "command": [
                "shutdown",
                "/r",
                "/t",
                "0",
            ],
            "check": True,
        }
    ]

    assert result == {
        "status": "restarting",
    }


def test_restart_reports_windows_failure(monkeypatch):
    monkeypatch.setattr(
        "device_agent.executor.platform.system",
        lambda: "Windows",
    )

    class FakeSubprocess:
        @staticmethod
        def run(command, check):
            raise RuntimeError("restart failed")

    monkeypatch.setattr(
        "device_agent.executor.subprocess",
        FakeSubprocess,
        raising=False,
    )

    executor = CommandExecutor()

    with pytest.raises(
        RuntimeError,
        match="restart failed",
    ):
        executor.execute("restart")
