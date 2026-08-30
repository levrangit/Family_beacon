import pytest

from device_agent.worker import DeviceAgentWorker


class FakeAPI:
    def __init__(self, recovered_commands):
        self.recovered_commands = recovered_commands
        self.calls = []

    def authenticate(self):
        self.calls.append("authenticate")
        return {
            "device_id": "test-device-001",
        }

    def recover_commands(self, stale_after_seconds=120):
        self.calls.append(stale_after_seconds)
        return self.recovered_commands


def test_recover_stale_commands_returns_recovered_commands(capsys):
    recovered = [
        {
            "id": "test-command-001",
            "command": "get_status",
            "status": "pending",
        }
    ]

    api = FakeAPI(recovered)

    worker = DeviceAgentWorker(api=api)

    result = worker.recover_stale_commands(
        stale_after_seconds=120,
    )

    assert result == recovered
    assert api.calls == [120]

    output = capsys.readouterr().out

    assert "CRASH RECOVERY: recovered 1 command(s)" in output
    assert "RECOVERED COMMAND: test-command-001 get_status" in output


def test_recover_stale_commands_when_nothing_is_stale(capsys):
    api = FakeAPI([])

    worker = DeviceAgentWorker(api=api)

    result = worker.recover_stale_commands(
        stale_after_seconds=120,
    )

    assert result == []
    assert api.calls == [120]

    output = capsys.readouterr().out

    assert "CRASH RECOVERY: no stale commands" in output


def test_run_performs_recovery_before_polling(monkeypatch, capsys):
    class StartupWorker(DeviceAgentWorker):
        def __init__(self):
            super().__init__(api=FakeAPI([]))
            self.events = []

        def recover_stale_commands(self, stale_after_seconds=120):
            self.events.append(("recover", stale_after_seconds))
            return []

        def run_once(self):
            self.events.append(("run_once",))
            raise KeyboardInterrupt

    worker = StartupWorker()

    with pytest.raises(KeyboardInterrupt):
        worker.run()

    assert worker.events == [
        ("recover", 120),
        ("run_once",),
    ]


def test_run_continues_when_recovery_fails(monkeypatch, capsys):
    class RecoveryFailureWorker(DeviceAgentWorker):
        def __init__(self):
            super().__init__(api=FakeAPI([]))
            self.events = []

        def recover_stale_commands(self, stale_after_seconds=120):
            self.events.append(("recover", stale_after_seconds))
            raise RuntimeError("recovery failed")

        def run_once(self):
            self.events.append(("run_once",))
            raise KeyboardInterrupt

    worker = RecoveryFailureWorker()

    with pytest.raises(KeyboardInterrupt):
        worker.run()

    assert worker.events == [
        ("recover", 120),
        ("run_once",),
    ]

    output = capsys.readouterr().out

    assert "CRASH RECOVERY ERROR: recovery failed" in output


def test_recovered_command_can_be_claimed_executed_and_completed():
    command = {
        "id": "recovered-command-001",
        "command": "get_status",
        "payload": {
            "recovery_test": "automatic",
        },
        "status": "executing",
    }

    class FullCycleAPI(FakeAPI):
        def __init__(self):
            super().__init__([])
            self.claimed = command
            self.completed = []

        def claim_command(self):
            claimed = self.claimed
            self.claimed = None
            return claimed

        def complete_command(
            self,
            command_id,
            status,
            result=None,
            error_message=None,
        ):
            self.completed.append(
                {
                    "command_id": command_id,
                    "status": status,
                    "result": result,
                    "error_message": error_message,
                }
            )

            return self.completed[-1]

    api = FullCycleAPI()

    worker = DeviceAgentWorker(api=api)

    processed = worker.run_once()

    assert processed is True

    assert api.completed == [
        {
            "command_id": "recovered-command-001",
            "status": "completed",
            "result": {
                "status": "online",
            },
            "error_message": None,
        }
    ]
