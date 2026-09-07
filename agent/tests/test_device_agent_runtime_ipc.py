"""Unit tests for Device Agent runtime IPC routing."""

from __future__ import annotations

from agent.device_agent.service.runtime import AgentRuntime


class FakeNamedPipeIPCServer:
    def __init__(self, handler):
        self.handler = handler
        self.endpoint = r"\\.\pipe\family-beacon"
        self.started = False
        self.stopped = False

    def start(self) -> None:
        self.started = True

    def stop(self) -> None:
        self.stopped = True


def test_runtime_starts_and_stops_ipc_server(monkeypatch) -> None:
    monkeypatch.setattr(
        "agent.device_agent.service.runtime.NamedPipeIPCServer",
        FakeNamedPipeIPCServer,
    )

    runtime = AgentRuntime()
    runtime.start()

    assert runtime.ipc_server is not None
    assert runtime.ipc_server.started is True

    runtime.stop()

    assert runtime.ipc_server is None


def test_runtime_handles_status_request(monkeypatch) -> None:
    monkeypatch.setattr(
        "agent.device_agent.service.runtime.NamedPipeIPCServer",
        FakeNamedPipeIPCServer,
    )

    runtime = AgentRuntime()
    response = runtime.handle_ipc_request({"type": "status"})

    assert response == {
        "ok": True,
        "type": "status",
        "service": "running",
        "registration_active": False,
    }


def test_runtime_handles_local_registration_start_and_cancel(monkeypatch) -> None:
    monkeypatch.setattr(
        "agent.device_agent.service.runtime.NamedPipeIPCServer",
        FakeNamedPipeIPCServer,
    )

    runtime = AgentRuntime()
    started = runtime.handle_ipc_request({"type": "registration.start"})

    assert started["ok"] is True
    assert started["type"] == "registration.start"
    assert started["request_id"]
    assert started["registration_code"]
    assert started["expires_at"]

    status = runtime.handle_ipc_request({"type": "status"})
    assert status["registration_active"] is True

    cancelled = runtime.handle_ipc_request({"type": "registration.cancel"})
    assert cancelled == {"ok": True, "type": "registration.cancel"}

    status = runtime.handle_ipc_request({"type": "status"})
    assert status["registration_active"] is False


def test_runtime_rejects_unsupported_ipc_message() -> None:
    runtime = AgentRuntime()

    assert runtime.handle_ipc_request({"type": "unknown"}) == {
        "ok": False,
        "error": "unsupported_message_type",
    }
