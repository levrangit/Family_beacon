"""RED tests for Tray <-> Device Agent Service IPC."""

from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

from agent.device_agent.tray.ipc_client import IPCClient
from agent.device_agent.ipc.server import IPCServer


def test_ipc_client_can_connect_to_service() -> None:
    server = IPCServer()
    server.start()
    try:
        client = IPCClient(server.endpoint)
        assert client.connect() is True
    finally:
        server.stop()


def test_ipc_client_can_send_request_and_receive_response() -> None:
    server = IPCServer()
    server.start()
    try:
        client = IPCClient(server.endpoint)
        client.connect()

        response = client.request({"type": "status"})

        assert response == {"ok": True, "type": "status"}
    finally:
        server.stop()


def test_ipc_request_has_defined_message_shape() -> None:
    server = IPCServer()
    server.start()
    try:
        client = IPCClient(server.endpoint)
        client.connect()

        response = client.request({"type": "ping"})

        assert isinstance(response, dict)
        assert response["ok"] is True
        assert response["type"] == "ping"
    finally:
        server.stop()


def test_ipc_client_reports_service_unavailable() -> None:
    client = IPCClient("family-beacon-test-unavailable")

    with pytest.raises(ConnectionError):
        client.connect()


def test_ipc_client_does_not_require_backend_or_supabase_credentials() -> None:
    client = IPCClient("family-beacon-test")

    assert client.requires_backend is False
    assert client.requires_supabase is False
