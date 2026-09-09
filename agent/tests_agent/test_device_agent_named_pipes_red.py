"""RED tests for Windows Named Pipes IPC."""

from __future__ import annotations

import os

import pytest

if os.name != "nt":
    pytestmark = pytest.mark.skip(reason="Windows Named Pipes are Windows-only")


@pytest.mark.skipif(os.name != "nt", reason="Windows Named Pipes are Windows-only")
def test_named_pipe_server_exposes_pipe_endpoint() -> None:
    from agent.device_agent.ipc.named_pipe_server import NamedPipeIPCServer

    server = NamedPipeIPCServer()
    try:
        assert server.endpoint.startswith("\\\\.\\pipe\\family-beacon")
        server.start()
    finally:
        server.stop()


@pytest.mark.skipif(os.name != "nt", reason="Windows Named Pipes are Windows-only")
def test_named_pipe_client_connects_to_service() -> None:
    from agent.device_agent.ipc.named_pipe_client import NamedPipeIPCClient
    from agent.device_agent.ipc.named_pipe_server import NamedPipeIPCServer

    server = NamedPipeIPCServer()
    server.start()
    try:
        client = NamedPipeIPCClient(server.endpoint)
        assert client.connect() is True
        client.close()
    finally:
        server.stop()


@pytest.mark.skipif(os.name != "nt", reason="Windows Named Pipes are Windows-only")
def test_named_pipe_client_sends_request_and_receives_response() -> None:
    from agent.device_agent.ipc.named_pipe_client import NamedPipeIPCClient
    from agent.device_agent.ipc.named_pipe_server import NamedPipeIPCServer

    server = NamedPipeIPCServer()
    server.start()
    try:
        client = NamedPipeIPCClient(server.endpoint)
        client.connect()

        response = client.request({"type": "status"})

        assert response == {"ok": True, "type": "status"}
        client.close()
    finally:
        server.stop()


@pytest.mark.skipif(os.name != "nt", reason="Windows Named Pipes are Windows-only")
def test_named_pipe_client_reports_service_unavailable() -> None:
    from agent.device_agent.ipc.named_pipe_client import NamedPipeIPCClient

    client = NamedPipeIPCClient(r"\\.\pipe\family-beacon-unavailable")

    with pytest.raises(ConnectionError):
        client.connect()


@pytest.mark.skipif(os.name != "nt", reason="Windows Named Pipes are Windows-only")
def test_named_pipe_ipc_does_not_require_backend_or_supabase_credentials() -> None:
    from agent.device_agent.ipc.named_pipe_client import NamedPipeIPCClient

    client = NamedPipeIPCClient(r"\\.\pipe\family-beacon-test")

    assert client.requires_backend is False
    assert client.requires_supabase is False
