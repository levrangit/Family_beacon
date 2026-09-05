from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.update_decision import check_device_update


def _device_table(data):
    table = MagicMock()
    table.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value.data = data
    return table


def _release_table(data):
    table = MagicMock()
    table.select.return_value.eq.return_value.lte.return_value.execute.return_value.data = data
    return table


def _compatibility_table(data):
    table = MagicMock()
    table.select.return_value.eq.return_value.in_.return_value.execute.return_value.data = data
    return table


def test_check_device_update_selects_highest_compatible_release(monkeypatch):
    client = MagicMock()
    client.table.side_effect = [
        _device_table({
            "id": "device-1",
            "platform": "windows",
            "agent_version": "1.0.0",
            "target_agent_version": None,
            "update_status": "idle",
        }),
        _release_table([
            {"id": "release-1", "component": "agent", "version": "1.1.0", "artifact_ref": "a", "checksum": "c", "release_notes": None},
            {"id": "release-2", "component": "agent", "version": "1.2.0", "artifact_ref": "b", "checksum": "d", "release_notes": "new"},
        ]),
        _compatibility_table([
            {"id": "compat-1", "release_id": "release-1", "platform": "windows", "min_agent_version": None, "max_agent_version": None},
            {"id": "compat-2", "release_id": "release-2", "platform": "windows", "min_agent_version": "1.0.0", "max_agent_version": None},
        ]),
    ]
    monkeypatch.setattr("app.update_decision.get_user_client", lambda token: client)

    result = check_device_update("token", "device-1")

    assert result["update_available"] is True
    assert result["current_version"] == "1.0.0"
    assert result["target_version"] == "1.2.0"
    assert result["release_id"] == "release-2"


def test_check_device_update_rejects_incompatible_release(monkeypatch):
    client = MagicMock()
    client.table.side_effect = [
        _device_table({
            "id": "device-1",
            "platform": "windows",
            "agent_version": "1.0.0",
            "target_agent_version": None,
            "update_status": "idle",
        }),
        _release_table([
            {"id": "release-1", "component": "agent", "version": "2.0.0", "artifact_ref": "a", "checksum": "c", "release_notes": None},
        ]),
        _compatibility_table([
            {"id": "compat-1", "release_id": "release-1", "platform": "windows", "min_agent_version": None, "max_agent_version": "1.5.0"},
        ]),
    ]
    monkeypatch.setattr("app.update_decision.get_user_client", lambda token: client)

    result = check_device_update("token", "device-1")

    assert result["update_available"] is False
    assert result["reason"] == "no_compatible_update"


def test_check_device_update_handles_unknown_agent_version(monkeypatch):
    client = MagicMock()
    client.table.side_effect = [
        _device_table({
            "id": "device-1",
            "platform": "windows",
            "agent_version": None,
            "target_agent_version": None,
            "update_status": "idle",
        }),
    ]
    monkeypatch.setattr("app.update_decision.get_user_client", lambda token: client)

    result = check_device_update("token", "device-1")

    assert result["update_available"] is False
    assert result["reason"] == "agent_version_unknown"


def test_check_device_update_returns_404_when_device_is_missing(monkeypatch):
    client = MagicMock()
    client.table.side_effect = [_device_table(None)]
    monkeypatch.setattr("app.update_decision.get_user_client", lambda token: client)

    with pytest.raises(HTTPException) as exc:
        check_device_update("token", "missing")

    assert exc.value.status_code == 404
    assert exc.value.detail == "Device not found"
