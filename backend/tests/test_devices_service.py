from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.devices import (
    CreateDeviceRequest,
    UpdateDeviceRequest,
    create_device,
    delete_device,
    get_device,
    get_device_status,
    heartbeat_device,
    list_devices,
    update_device,
)


def _client():
    return MagicMock()


def test_create_device_returns_device(monkeypatch):
    client = _client()
    client.table.return_value.insert.return_value.execute.return_value.data = [{"id": "device-1"}]
    monkeypatch.setattr("app.devices.get_user_client", lambda token: client)

    request = CreateDeviceRequest(
        child_id="child-1", device_id="machine-1", name="Laptop", platform="linux"
    )
    result = create_device("token", request)

    assert result["id"] == "device-1"


def test_create_device_maps_duplicate_to_409(monkeypatch):
    client = _client()
    client.table.return_value.insert.return_value.execute.side_effect = RuntimeError("duplicate key value")
    monkeypatch.setattr("app.devices.get_user_client", lambda token: client)

    request = CreateDeviceRequest(
        child_id="child-1", device_id="machine-1", name="Laptop", platform="linux"
    )
    with pytest.raises(HTTPException) as exc:
        create_device("token", request)
    assert exc.value.status_code == 409


def test_list_devices_adds_status(monkeypatch):
    now = datetime.now(timezone.utc).isoformat()
    client = _client()
    client.table.return_value.select.return_value.order.return_value.execute.return_value.data = [
        {"id": "device-1", "last_seen": now}
    ]
    monkeypatch.setattr("app.devices.get_user_client", lambda token: client)

    result = list_devices("token")

    assert result[0]["status"] == "online"


def test_get_device_returns_404_when_missing(monkeypatch):
    client = _client()
    client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
    monkeypatch.setattr("app.devices.get_user_client", lambda token: client)

    with pytest.raises(HTTPException) as exc:
        get_device("token", "missing")
    assert exc.value.status_code == 404


def test_update_device_rejects_empty_update(monkeypatch):
    client = _client()
    monkeypatch.setattr("app.devices.get_user_client", lambda token: client)

    with pytest.raises(HTTPException) as exc:
        update_device("token", "device-1", UpdateDeviceRequest())
    assert exc.value.status_code == 400
    assert exc.value.detail == "No fields to update"


def test_update_device_returns_updated_device(monkeypatch):
    client = _client()
    client.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [
        {"id": "device-1", "name": "New name"}
    ]
    monkeypatch.setattr("app.devices.get_user_client", lambda token: client)

    result = update_device("token", "device-1", UpdateDeviceRequest(name="New name"))

    assert result["name"] == "New name"


def test_heartbeat_device_maps_missing_device(monkeypatch):
    client = _client()
    client.rpc.return_value.execute.return_value.data = None
    monkeypatch.setattr("app.devices.get_user_client", lambda token: client)

    with pytest.raises(HTTPException) as exc:
        heartbeat_device("token", "missing")
    assert exc.value.status_code == 404


def test_delete_device_returns_deleted_marker(monkeypatch):
    client = _client()
    client.table.return_value.delete.return_value.eq.return_value.execute.return_value.data = [
        {"id": "device-1"}
    ]
    monkeypatch.setattr("app.devices.get_user_client", lambda token: client)

    result = delete_device("token", "device-1")

    assert result == {"deleted": True, "device_id": "device-1"}


def test_get_device_status_rejects_invalid_timestamp():
    assert get_device_status("not-a-date") == "offline"


def test_get_device_status_accepts_z_timestamp():
    timestamp = (
        datetime.now(timezone.utc) - timedelta(seconds=30)
    ).isoformat().replace("+00:00", "Z")
    assert get_device_status(timestamp) == "online"
