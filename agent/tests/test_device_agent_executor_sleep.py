import pytest

from device_agent.executor import CommandExecutor


def test_sleep_is_supported():
    assert "sleep" in CommandExecutor.SUPPORTED_COMMANDS


def test_sleep_rejected_on_non_windows(monkeypatch):
    monkeypatch.setattr(
        "device_agent.executor.platform.system",
        lambda: "Linux",
    )

    executor = CommandExecutor()

    with pytest.raises(
        RuntimeError,
        match="supported only on Windows",
    ):
        executor.execute("sleep")


def test_sleep_calls_windows_sleep(monkeypatch):
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

    result = executor.execute("sleep")

    assert calls == [
        {
            "command": [
                "rundll32.exe",
                "powrprof.dll,SetSuspendState",
                "0",
                "1",
                "0",
            ],
            "check": True,
        }
    ]

    assert result == {
        "status": "sleeping",
    }


def test_sleep_reports_windows_failure(monkeypatch):
    monkeypatch.setattr(
        "device_agent.executor.platform.system",
        lambda: "Windows",
    )

    class FakeSubprocess:
        @staticmethod
        def run(command, check):
            raise RuntimeError("sleep failed")

    monkeypatch.setattr(
        "device_agent.executor.subprocess",
        FakeSubprocess,
        raising=False,
    )

    executor = CommandExecutor()

    with pytest.raises(
        RuntimeError,
        match="sleep failed",
    ):
        executor.execute("sleep")
