"""Unit tests for Device Agent runtime IPC routing."""

from __future__ import annotations

from agent.device_agent.backend_client import BackendClientError
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


class FakeBackendClient:
    def __init__(self):
        self.created = []

    def create_device_registration_request(self, **kwargs):
        self.created.append(kwargs)
        return {
            "request_id": "request-001",
            "registration_code": "ABCD-2345",
            "status": "pending",
            "expires_at": "2030-01-01T00:10:00+00:00",
        }


def test_runtime_starts_and_stops_ipc_server(monkeypatch) -> None:
    monkeypatch.setattr(
        "agent.device_agent.service.runtime.NamedPipeIPCServer",
        FakeNamedPipeIPCServer,
    )

    runtime = AgentRuntime(backend_client=FakeBackendClient())
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

    runtime = AgentRuntime(backend_client=FakeBackendClient())
    response = runtime.handle_ipc_request({"type": "status"})

    assert response == {
        "ok": True,
        "type": "status",
        "service": "running",
        "registration_active": False,
    }


def test_runtime_creates_backend_registration_and_cancels_local_state(monkeypatch) -> None:
    monkeypatch.setattr(
        "agent.device_agent.service.runtime.NamedPipeIPCServer",
        FakeNamedPipeIPCServer,
    )

    backend = FakeBackendClient()
    runtime = AgentRuntime(backend_client=backend)
    started = runtime.handle_ipc_request({"type": "registration.start"})

    assert started == {
        "ok": True,
        "type": "registration.start",
        "request_id": "request-001",
        "registration_code": "ABCD-2345",
        "expires_at": "2030-01-01T00:10:00+00:00",
    }
    assert backend.created
    assert backend.created[0]["platform"]
    assert backend.created[0]["device_id"]

    status = runtime.handle_ipc_request({"type": "status"})
    assert status["registration_active"] is True

    cancelled = runtime.handle_ipc_request({"type": "registration.cancel"})
    assert cancelled == {"ok": True, "type": "registration.cancel"}

    status = runtime.handle_ipc_request({"type": "status"})
    assert status["registration_active"] is False


def test_runtime_reports_backend_failure(monkeypatch) -> None:
    monkeypatch.setattr(
        "agent.device_agent.service.runtime.NamedPipeIPCServer",
        FakeNamedPipeIPCServer,
    )

    class FailingBackendClient(FakeBackendClient):
        def create_device_registration_request(self, **kwargs):
            raise BackendClientError("backend unavailable")

    runtime = AgentRuntime(backend_client=FailingBackendClient())
    response = runtime.handle_ipc_request({"type": "registration.start"})

    assert response == {
        "ok": False,
        "type": "registration.start",
        "error": "registration_backend_unavailable",
    }


def test_runtime_rejects_unsupported_ipc_message() -> None:
    runtime = AgentRuntime(backend_client=FakeBackendClient())

    assert runtime.handle_ipc_request({"type": "unknown"}) == {
        "ok": False,
        "error": "unsupported_message_type",
    }
