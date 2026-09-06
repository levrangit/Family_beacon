from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.commands import CreateCommandRequest, create_command, get_command, list_commands


def _client():
    return MagicMock()


def test_create_command_calls_rpc_with_payload(monkeypatch):
    client = _client()
    client.rpc.return_value.execute.return_value.data = {"id": "command-1", "status": "pending"}
    monkeypatch.setattr("app.commands.get_user_client", lambda token: client)

    request = CreateCommandRequest(device_id="device-1", command="lock", payload={"reason": "limit"})
    result = create_command("token", request)

    assert result["id"] == "command-1"
    client.rpc.assert_called_once_with(
        "create_command",
        {
            "target_device_id": "device-1",
            "target_command": "lock",
            "target_payload": {"reason": "limit"},
        },
    )


@pytest.mark.parametrize(
    ("message", "status", "detail"),
    [
        ("Permission denied", 403, "You do not have permission to create this command"),
        ("Device not found", 404, "Device not found"),
    ],
)
def test_create_command_maps_expected_errors(monkeypatch, message, status, detail):
    client = _client()
    client.rpc.return_value.execute.side_effect = RuntimeError(message)
    monkeypatch.setattr("app.commands.get_user_client", lambda token: client)

    request = CreateCommandRequest(device_id="device-1", command="lock")
    with pytest.raises(HTTPException) as exc:
        create_command("token", request)

    assert exc.value.status_code == status
    assert exc.value.detail == detail


def test_create_command_maps_empty_result_to_500(monkeypatch):
    client = _client()
    client.rpc.return_value.execute.return_value.data = None
    monkeypatch.setattr("app.commands.get_user_client", lambda token: client)

    with pytest.raises(HTTPException) as exc:
        create_command("token", CreateCommandRequest(device_id="device-1", command="lock"))

    assert exc.value.status_code == 500


def test_list_commands_without_device_filter(monkeypatch):
    client = _client()
    client.table.return_value.select.return_value.order.return_value.execute.return_value.data = [
        {"id": "command-1", "device_id": "device-1"}
    ]
    monkeypatch.setattr("app.commands.get_user_client", lambda token: client)

    result = list_commands("token")

    assert result == [{"id": "command-1", "device_id": "device-1"}]
    client.table.return_value.select.return_value.order.assert_called_once_with("created_at", desc=True)


def test_list_commands_with_device_filter(monkeypatch):
    client = _client()
    query = client.table.return_value.select.return_value.order.return_value
    query.eq.return_value.execute.return_value.data = [{"id": "command-1", "device_id": "device-1"}]
    monkeypatch.setattr("app.commands.get_user_client", lambda token: client)

    result = list_commands("token", "device-1")

    assert result[0]["device_id"] == "device-1"
    query.eq.assert_called_once_with("device_id", "device-1")


def test_get_command_returns_404_when_missing(monkeypatch):
    client = _client()
    client.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value.data = []
    monkeypatch.setattr("app.commands.get_user_client", lambda token: client)

    with pytest.raises(HTTPException) as exc:
        get_command("token", "missing")

    assert exc.value.status_code == 404
    assert exc.value.detail == "Command not found"


def test_get_command_returns_command(monkeypatch):
    client = _client()
    client.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value.data = [
        {"id": "command-1", "device_id": "device-1"}
    ]
    monkeypatch.setattr("app.commands.get_user_client", lambda token: client)

    assert get_command("token", "command-1")["id"] == "command-1"
