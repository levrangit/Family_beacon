from datetime import date
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.time_usage import RecordTimeUsageRequest, list_time_usage, record_time_usage


def test_record_time_usage_rejects_negative_minutes_without_database(monkeypatch):
    client = MagicMock()
    monkeypatch.setattr("app.time_usage.get_user_client", lambda token: client)

    request = RecordTimeUsageRequest(
        child_id="child-1", usage_date=date(2026, 9, 2), additional_minutes=-1
    )
    with pytest.raises(HTTPException) as exc:
        record_time_usage("token", "device-1", request)

    assert exc.value.status_code == 400
    client.rpc.assert_not_called()


def test_record_time_usage_calls_rpc_with_expected_values(monkeypatch):
    client = MagicMock()
    client.rpc.return_value.execute.return_value.data = {"used_minutes": 30}
    monkeypatch.setattr("app.time_usage.get_user_client", lambda token: client)

    request = RecordTimeUsageRequest(
        child_id="child-1", usage_date=date(2026, 9, 2), additional_minutes=30
    )
    result = record_time_usage("token", "device-1", request)

    assert result == {"used_minutes": 30}
    client.rpc.assert_called_once_with(
        "record_time_usage",
        {
            "target_child_id": "child-1",
            "target_device_id": "device-1",
            "target_usage_date": "2026-09-02",
            "additional_minutes": 30,
        },
    )


@pytest.mark.parametrize(
    ("message", "status", "detail"),
    [
        ("Device not found", 404, "Device not found"),
        ("Device does not belong to child", 400, "Device does not belong to child"),
        ("Permission denied", 403, "You do not have permission to record time usage"),
    ],
)
def test_record_time_usage_maps_expected_errors(monkeypatch, message, status, detail):
    client = MagicMock()
    client.rpc.return_value.execute.side_effect = RuntimeError(message)
    monkeypatch.setattr("app.time_usage.get_user_client", lambda token: client)

    request = RecordTimeUsageRequest(
        child_id="child-1", usage_date=date(2026, 9, 2), additional_minutes=30
    )
    with pytest.raises(HTTPException) as exc:
        record_time_usage("token", "device-1", request)

    assert exc.value.status_code == status
    assert exc.value.detail == detail


def test_list_time_usage_filters_by_child_and_date(monkeypatch):
    client = MagicMock()
    query = client.table.return_value.select.return_value
    query.eq.return_value.eq.return_value.order.return_value.execute.return_value.data = [
        {"child_id": "child-1", "usage_date": "2026-09-02", "used_minutes": 30}
    ]
    monkeypatch.setattr("app.time_usage.get_user_client", lambda token: client)

    result = list_time_usage("token", "child-1", date(2026, 9, 2))

    assert result[0]["child_id"] == "child-1"
    query.eq.assert_called_once_with("child_id", "child-1")
