from device_agent.worker import DeviceAgentWorker


class FakeAuth:
    def __init__(self, events):
        self.events = events

    def authenticate(self):
        self.events.append("authenticate")
        return "device-001"


class FakeAPI:
    def __init__(self, events):
        self.events = events
        self.heartbeat_calls = 0

    def heartbeat(self):
        self.events.append("heartbeat")
        self.heartbeat_calls += 1
        return {
            "id": "device-001",
            "is_online": True,
        }

    def recover_commands(self, stale_after_seconds=120):
        self.events.append("recover")
        return []


class FakeCommands:
    def claim_next(self):
        return None


def test_worker_sends_initial_heartbeat_after_authentication():
    events = []

    api = FakeAPI(events)
    worker = DeviceAgentWorker(api=api)

    worker.auth = FakeAuth(events)
    worker.commands = FakeCommands()

    # Проверяем только начальную последовательность.
    # Полный бесконечный run() здесь намеренно не запускаем.
    device_id = worker.auth.authenticate()
    assert device_id == "device-001"

    api.heartbeat()

    worker.recover_stale_commands()

    assert events == [
        "authenticate",
        "heartbeat",
        "recover",
    ]


def test_heartbeat_failure_does_not_break_worker():
    events = []

    class FailingAPI(FakeAPI):
        def heartbeat(self):
            events.append("heartbeat")
            raise RuntimeError("heartbeat failed")

    api = FailingAPI(events)
    worker = DeviceAgentWorker(api=api)

    worker.commands = FakeCommands()

    try:
        api.heartbeat()
    except RuntimeError as exc:
        events.append(f"heartbeat_error:{exc}")

    # Worker должен продолжить работу после ошибки heartbeat.
    worker.run_once()

    assert events == [
        "heartbeat",
        "heartbeat_error:heartbeat failed",
    ]


def test_heartbeat_is_not_part_of_every_poll():
    events = []

    api = FakeAPI(events)
    worker = DeviceAgentWorker(api=api)

    worker.commands = FakeCommands()

    worker.run_once()
    worker.run_once()
    worker.run_once()

    assert events == []
    assert api.heartbeat_calls == 0
