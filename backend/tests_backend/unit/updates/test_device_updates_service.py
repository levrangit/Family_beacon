from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.device_updates import get_device_update, list_device_updates


def _client():
    return MagicMock()


def test_list_device_updates_returns_history(monkeypatch):
    client = _client()
    client.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value.data = [
        {"id": "update-1", "device_id": "device-1", "status": "success"}
    ]
    monkeypatch.setattr("app.device_updates.get_user_client", lambda token: client)

    result = list_device_updates("token", "device-1")

    assert result == [
        {"id": "update-1", "device_id": "device-1", "status": "success"}
    ]
    client.table.assert_called_once_with("device_updates")


def test_get_device_update_returns_404_when_missing(monkeypatch):
    client = _client()
    client.table.return_value.select.return_value.eq.return_value.eq.return_value.maybe_single.return_value.execute.return_value.data = None
    monkeypatch.setattr("app.device_updates.get_user_client", lambda token: client)

    with pytest.raises(HTTPException) as exc:
        get_device_update("token", "device-1", "missing")

    assert exc.value.status_code == 404
    assert exc.value.detail == "Device update not found"
