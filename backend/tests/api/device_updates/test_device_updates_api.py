import pytest

from app.main import (
    app,
    get_device_update_endpoint,
    list_device_updates_endpoint,
)


@pytest.mark.anyio
async def test_list_device_updates_endpoint_forwards_authenticated_token(monkeypatch):
    calls = []

    def fake_list_device_updates(access_token, device_id):
        calls.append((access_token, device_id))
        return [{"id": "update-1", "device_id": device_id, "status": "success"}]

    monkeypatch.setattr("app.main.list_device_updates", fake_list_device_updates)

    result = await list_device_updates_endpoint(
        device_id="device-1",
        auth=(object(), "access-token"),
    )

    assert result == [
        {"id": "update-1", "device_id": "device-1", "status": "success"}
    ]
    assert calls == [("access-token", "device-1")]


@pytest.mark.anyio
async def test_get_device_update_endpoint_forwards_authenticated_token(monkeypatch):
    calls = []

    def fake_get_device_update(access_token, device_id, update_id):
        calls.append((access_token, device_id, update_id))
        return {
            "id": update_id,
            "device_id": device_id,
            "status": "success",
        }

    monkeypatch.setattr("app.main.get_device_update", fake_get_device_update)

    result = await get_device_update_endpoint(
        device_id="device-1",
        update_id="update-1",
        auth=(object(), "access-token"),
    )

    assert result == {
        "id": "update-1",
        "device_id": "device-1",
        "status": "success",
    }
    assert calls == [("access-token", "device-1", "update-1")]


def test_device_update_history_routes_are_registered():
    routes = {
        (route.path, method)
        for route in app.routes
        for method in getattr(route, "methods", set())
    }

    assert ("/devices/{device_id}/updates", "GET") in routes
    assert ("/devices/{device_id}/updates/{update_id}", "GET") in routes
