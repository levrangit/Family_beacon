import pytest

from app.main import app, check_device_update_endpoint, list_releases_endpoint


@pytest.mark.anyio
async def test_list_releases_endpoint_forwards_authenticated_token(monkeypatch):
    calls = []

    def fake_list_releases(access_token):
        calls.append(access_token)
        return [{"id": "release-1", "component": "agent", "version": "1.2.0"}]

    monkeypatch.setattr("app.main.list_releases", fake_list_releases)

    result = await list_releases_endpoint(auth=(object(), "access-token"))

    assert result == [
        {"id": "release-1", "component": "agent", "version": "1.2.0"}
    ]
    assert calls == ["access-token"]


@pytest.mark.anyio
async def test_update_check_endpoint_forwards_authenticated_token(monkeypatch):
    calls = []

    def fake_check_device_update(access_token, device_id):
        calls.append((access_token, device_id))
        return {
            "update_available": True,
            "device_id": device_id,
            "target_version": "1.2.0",
        }

    monkeypatch.setattr("app.main.check_device_update", fake_check_device_update)

    result = await check_device_update_endpoint(
        device_id="device-1",
        auth=(object(), "access-token"),
    )

    assert result == {
        "update_available": True,
        "device_id": "device-1",
        "target_version": "1.2.0",
    }
    assert calls == [("access-token", "device-1")]


def test_pr3_routes_are_registered():
    routes = {
        (route.path, method)
        for route in app.routes
        for method in getattr(route, "methods", set())
    }

    assert ("/releases", "GET") in routes
    assert ("/devices/{device_id}/update-check", "GET") in routes
