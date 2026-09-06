from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app.device_agent import DeviceHeartbeatRequest, device_heartbeat


def test_heartbeat_request_normalizes_agent_version():
    request = DeviceHeartbeatRequest(agent_version=" 0.3.1 ")

    assert request.agent_version == "0.3.1"


def test_heartbeat_request_rejects_blank_agent_version():
    with pytest.raises(ValidationError):
        DeviceHeartbeatRequest(agent_version="   ")


def test_heartbeat_request_rejects_unknown_fields():
    with pytest.raises(ValidationError):
        DeviceHeartbeatRequest(
            agent_version="0.3.1",
            update_status="idle",
        )


def test_device_heartbeat_reports_agent_version(monkeypatch):
    client = MagicMock()
    client.rpc.return_value.execute.return_value.data = {
        "id": "device-001",
        "agent_version": "0.3.1",
        "is_online": True,
        "update_status": "idle",
        "target_agent_version": None,
    }

    monkeypatch.setattr("app.device_agent.supabase", client)
    monkeypatch.setattr(
        "app.device_agent.get_device_token_hash",
        lambda authorization: "hashed-device-token",
    )

    result = device_heartbeat(
        data=DeviceHeartbeatRequest(agent_version="0.3.1"),
        authorization="Bearer test-token",
    )

    assert result["agent_version"] == "0.3.1"
    client.rpc.assert_called_once_with(
        "device_heartbeat_by_token_v2",
        {
            "target_token_hash": "hashed-device-token",
            "reported_agent_version": "0.3.1",
        },
    )


def test_device_heartbeat_maps_invalid_token(monkeypatch):
    client = MagicMock()
    client.rpc.return_value.execute.side_effect = RuntimeError(
        "Invalid device token"
    )

    monkeypatch.setattr("app.device_agent.supabase", client)
    monkeypatch.setattr(
        "app.device_agent.get_device_token_hash",
        lambda authorization: "hashed-device-token",
    )

    with pytest.raises(HTTPException) as exc:
        device_heartbeat(
            data=DeviceHeartbeatRequest(agent_version="0.3.1"),
            authorization="Bearer test-token",
        )

    assert exc.value.status_code == 401
