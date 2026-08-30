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
