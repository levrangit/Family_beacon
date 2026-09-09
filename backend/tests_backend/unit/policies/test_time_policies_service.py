from datetime import time
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.time_policies import (
    CreateTimePolicyRequest,
    UpdateTimePolicyRequest,
    create_time_policy,
    delete_time_policy,
    get_time_policy,
    list_time_policies,
    update_time_policy,
)


def _client():
    return MagicMock()


def test_create_time_policy_returns_policy(monkeypatch):
    client = _client()
    client.table.return_value.insert.return_value.execute.return_value.data = [{"id": "policy-1"}]
    monkeypatch.setattr("app.time_policies.get_user_client", lambda token: client)

    request = CreateTimePolicyRequest(
        child_id="child-1", day_of_week=1, daily_limit_minutes=120,
        start_time=time(8, 0), end_time=time(20, 0)
    )
    result = create_time_policy("token", request)

    assert result["id"] == "policy-1"
    args = client.table.return_value.insert.call_args.args[0]
    assert args["start_time"] == "08:00:00"
    assert args["end_time"] == "20:00:00"


def test_create_time_policy_maps_duplicate_to_409(monkeypatch):
    client = _client()
    client.table.return_value.insert.return_value.execute.side_effect = RuntimeError("duplicate key")
    monkeypatch.setattr("app.time_policies.get_user_client", lambda token: client)

    request = CreateTimePolicyRequest(child_id="child-1", day_of_week=1, daily_limit_minutes=120)
    with pytest.raises(HTTPException) as exc:
        create_time_policy("token", request)
    assert exc.value.status_code == 409


def test_list_time_policies_returns_policies(monkeypatch):
    data = [{"id": "policy-1", "child_id": "child-1", "day_of_week": 1}]
    client = _client()
    client.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value.data = data
    monkeypatch.setattr("app.time_policies.get_user_client", lambda token: client)

    assert list_time_policies("token", "child-1") == data


def test_get_time_policy_returns_404_when_missing(monkeypatch):
    client = _client()
    client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
    monkeypatch.setattr("app.time_policies.get_user_client", lambda token: client)

    with pytest.raises(HTTPException) as exc:
        get_time_policy("token", "missing")
    assert exc.value.status_code == 404


def test_update_time_policy_serializes_time_values(monkeypatch):
    client = _client()
    client.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [
        {"id": "policy-1", "start_time": "09:00:00"}
    ]
    monkeypatch.setattr("app.time_policies.get_user_client", lambda token: client)

    result = update_time_policy(
        "token", "policy-1", UpdateTimePolicyRequest(start_time=time(9, 0))
    )

    assert result["id"] == "policy-1"
    updates = client.table.return_value.update.call_args.args[0]
    assert updates["start_time"] == "09:00:00"


def test_update_time_policy_rejects_empty_update(monkeypatch):
    client = _client()
    monkeypatch.setattr("app.time_policies.get_user_client", lambda token: client)

    with pytest.raises(HTTPException) as exc:
        update_time_policy("token", "policy-1", UpdateTimePolicyRequest())
    assert exc.value.status_code == 400


def test_delete_time_policy_returns_deleted_marker(monkeypatch):
    client = _client()
    client.table.return_value.delete.return_value.eq.return_value.execute.return_value.data = [
        {"id": "policy-1"}
    ]
    monkeypatch.setattr("app.time_policies.get_user_client", lambda token: client)

    assert delete_time_policy("token", "policy-1") == {
        "deleted": True,
        "policy_id": "policy-1",
    }
