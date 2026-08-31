import pytest

from device_agent.executor import CommandExecutor
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


def test_unblocker_requires_app():
    blocker = WindowsAppBlocker()

    with pytest.raises(
        ValueError,
        match="app",
    ):
        blocker.unblock("")


def test_unblocker_rejects_non_windows(monkeypatch):
    monkeypatch.setattr(
        "device_agent.windows_app_blocker.platform.system",
        lambda: "Linux",
    )

    blocker = WindowsAppBlocker()

    with pytest.raises(
        RuntimeError,
        match="supported only on Windows",
    ):
        blocker.unblock("notepad.exe")


def test_unblocker_calls_windows_rule(monkeypatch):
    monkeypatch.setattr(
        "device_agent.windows_app_blocker.platform.system",
        lambda: "Windows",
    )

    calls = []

    blocker = WindowsAppBlocker()

    monkeypatch.setattr(
        blocker,
        "_remove_block_rule",
        lambda app: calls.append(app),
    )

    result = blocker.unblock(
        "C:\\Windows\\System32\\notepad.exe"
    )

    assert calls == [
        "C:\\Windows\\System32\\notepad.exe",
    ]

    assert result == {
        "status": "app_unblocked",
        "app": "C:\\Windows\\System32\\notepad.exe",
    }


def test_executor_unblock_app_requires_app():
    executor = CommandExecutor()

    with pytest.raises(
        ValueError,
        match="app",
    ):
        executor.execute(
            "unblock_app",
            {},
        )


def test_executor_unblock_app_rejects_non_windows(monkeypatch):
    monkeypatch.setattr(
        "device_agent.executor.platform.system",
        lambda: "Linux",
    )

    executor = CommandExecutor()

    with pytest.raises(
        RuntimeError,
        match="supported only on Windows",
    ):
        executor.execute(
            "unblock_app",
            {"app": "notepad.exe"},
        )


def test_executor_unblock_app_returns_unblocked_application(monkeypatch):
    monkeypatch.setattr(
        "device_agent.executor.platform.system",
        lambda: "Windows",
    )

    monkeypatch.setattr(
        "device_agent.windows_app_blocker.platform.system",
        lambda: "Windows",
    )

    monkeypatch.setattr(
        WindowsAppBlocker,
        "_remove_block_rule",
        staticmethod(lambda app: None),
    )

    executor = CommandExecutor()

    result = executor.execute(
        "unblock_app",
        {"app": "notepad.exe"},
    )

    assert result == {
        "status": "app_unblocked",
        "app": "notepad.exe",
    }



def test_worker_executes_unblock_app_command():
    from device_agent.worker import DeviceAgentWorker

    calls = []

    class FakeCommands:
        def claim_next(self):
            return {
                "id": "command-1",
                "command": "unblock_app",
                "payload": {
                    "app": "notepad.exe",
                },
            }

        def complete(self, **kwargs):
            calls.append(("complete", kwargs))

    class FakeExecutor:
        def execute(self, command, payload):
            calls.append(("execute", command, payload))
            return {
                "status": "app_unblocked",
                "app": payload["app"],
            }

    worker = DeviceAgentWorker.__new__(DeviceAgentWorker)

    worker.commands = FakeCommands()
    worker.executor = FakeExecutor()

    result = worker.run_once()

    assert result is True

    assert calls == [
        (
            "execute",
            "unblock_app",
            {
                "app": "notepad.exe",
            },
        ),
        (
            "complete",
            {
                "command_id": "command-1",
                "status": "completed",
                "result": {
                    "status": "app_unblocked",
                    "app": "notepad.exe",
                },
            },
        ),
    ]
