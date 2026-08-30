import pytest

from device_agent.worker import DeviceAgentWorker


def test_run_sends_heartbeat_after_authentication(monkeypatch):
    events = []

    class FakeAPI:
        def heartbeat(self):
            events.append("heartbeat")
            return {"status": "online"}

        def recover_commands(self, stale_after_seconds=120):
            events.append("recover")
            return []

    class FakeAuth:
        def authenticate(self):
            events.append("authenticate")
            return "device-001"

    class FakeCommands:
        def claim_next(self):
            events.append("claim")
            raise KeyboardInterrupt

    worker = DeviceAgentWorker(api=FakeAPI())
    worker.auth = FakeAuth()
    worker.commands = FakeCommands()

    monkeypatch.setattr(
        "device_agent.worker.POLL_INTERVAL_SECONDS",
        0,
    )

    with pytest.raises(KeyboardInterrupt):
        worker.run()

    assert events[:2] == [
        "authenticate",
        "heartbeat",
    ]


def test_run_sends_periodic_heartbeat(monkeypatch):
    events = []

    class FakeClock:
        now = 0.0

        @classmethod
        def time(cls):
            return cls.now

        @classmethod
        def advance(cls, seconds):
            cls.now += seconds

    class FakeAPI:
        def heartbeat(self):
            events.append(
                ("heartbeat", FakeClock.time())
            )
            return {"status": "online"}

        def recover_commands(self, stale_after_seconds=120):
            return []

    class FakeAuth:
        def authenticate(self):
            return "device-001"

    class FakeCommands:
        def claim_next(self):
            # Продвигаем виртуальное время на один polling-интервал.
            FakeClock.advance(5)

            if FakeClock.time() >= 35:
                raise KeyboardInterrupt

            return None

    worker = DeviceAgentWorker(api=FakeAPI())
    worker.auth = FakeAuth()
    worker.commands = FakeCommands()

    monkeypatch.setattr(
        "device_agent.worker.time.time",
        FakeClock.time,
    )
    monkeypatch.setattr(
        "device_agent.worker.time.sleep",
        lambda seconds: None,
    )
    monkeypatch.setattr(
        "device_agent.worker.POLL_INTERVAL_SECONDS",
        5,
    )

    with pytest.raises(KeyboardInterrupt):
        worker.run()

    heartbeat_times = [
        timestamp
        for event, timestamp in events
        if event == "heartbeat"
    ]

    assert heartbeat_times[0] == 0.0
    assert heartbeat_times[-1] >= 30.0
    assert len(heartbeat_times) >= 2


def test_heartbeat_retries_after_temporary_failure(monkeypatch):
    events = []

    class FakeClock:
        now = 0.0

        @classmethod
        def time(cls):
            return cls.now

    class FakeAPI:
        heartbeat_calls = 0

        def heartbeat(self):
            self.heartbeat_calls += 1
            events.append(("heartbeat", self.heartbeat_calls))

            if self.heartbeat_calls == 2:
                raise RuntimeError("temporary backend failure")

            return {"status": "online"}

        def recover_commands(self, stale_after_seconds=120):
            return []

    class FakeAuth:
        def authenticate(self):
            return "device-001"

    class FakeCommands:
        calls = 0

        def claim_next(self):
            self.calls += 1
            FakeClock.now += 30

            if self.calls >= 4:
                raise KeyboardInterrupt

            return None

    api = FakeAPI()
    worker = DeviceAgentWorker(api=api)
    worker.auth = FakeAuth()
    worker.commands = FakeCommands()

    monkeypatch.setattr(
        "device_agent.worker.time.time",
        FakeClock.time,
    )
    monkeypatch.setattr(
        "device_agent.worker.time.sleep",
        lambda seconds: None,
    )
    monkeypatch.setattr(
        "device_agent.worker.POLL_INTERVAL_SECONDS",
        5,
    )

    with pytest.raises(KeyboardInterrupt):
        worker.run()

    assert events == [
        ("heartbeat", 1),
        ("heartbeat", 2),
        ("heartbeat", 3),
        ("heartbeat", 4),
    ]


def test_worker_continues_after_run_once_failure(monkeypatch):
    events = []

    class FakeAPI:
        def heartbeat(self):
            events.append("heartbeat")
            return {"status": "online"}

        def recover_commands(self, stale_after_seconds=120):
            return []

    class FakeAuth:
        def authenticate(self):
            events.append("authenticate")
            return "device-001"

    class ResilientWorker(DeviceAgentWorker):
        def run_once(self):
            events.append("run_once")

            if events.count("run_once") == 1:
                raise RuntimeError("temporary backend failure")

            raise KeyboardInterrupt

    worker = ResilientWorker(api=FakeAPI())
    worker.auth = FakeAuth()

    monkeypatch.setattr(
        "device_agent.worker.POLL_INTERVAL_SECONDS",
        0,
    )

    with pytest.raises(KeyboardInterrupt):
        worker.run()

    assert events == [
        "authenticate",
        "heartbeat",
        "run_once",
        "run_once",
    ]


def test_multiple_heartbeat_intervals_are_reached(monkeypatch):
    heartbeat_times = []

    class FakeClock:
        now = 0.0

        @classmethod
        def time(cls):
            return cls.now

    class FakeAPI:
        def heartbeat(self):
            heartbeat_times.append(FakeClock.time())
            return {"status": "online"}

        def recover_commands(self, stale_after_seconds=120):
            return []

    class FakeAuth:
        def authenticate(self):
            return "device-001"

    class FakeCommands:
        calls = 0

        def claim_next(self):
            self.calls += 1
            FakeClock.now += 5

            if self.calls >= 20:
                raise KeyboardInterrupt

            return None

    worker = DeviceAgentWorker(api=FakeAPI())
    worker.auth = FakeAuth()
    worker.commands = FakeCommands()

    monkeypatch.setattr(
        "device_agent.worker.time.time",
        FakeClock.time,
    )
    monkeypatch.setattr(
        "device_agent.worker.time.sleep",
        lambda seconds: None,
    )
    monkeypatch.setattr(
        "device_agent.worker.POLL_INTERVAL_SECONDS",
        5,
    )

    with pytest.raises(KeyboardInterrupt):
        worker.run()

    assert heartbeat_times == [
        0.0,
        30.0,
        60.0,
        90.0,
    ]
