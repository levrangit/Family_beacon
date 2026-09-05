from unittest.mock import MagicMock

from app.releases import CreateReleaseRequest, create_release, get_release, list_releases


def test_list_releases_returns_published_catalog(monkeypatch):
    client = MagicMock()
    client.table.return_value.select.return_value.order.return_value.execute.return_value.data = [
        {"id": "release-1", "component": "agent", "version": "1.2.0"}
    ]
    monkeypatch.setattr("app.releases.get_user_client", lambda token: client)

    result = list_releases("token")

    assert result == [
        {"id": "release-1", "component": "agent", "version": "1.2.0"}
    ]
    client.table.assert_called_once_with("component_releases")


def test_get_release_returns_404_when_missing(monkeypatch):
    client = MagicMock()
    client.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value.data = None
    monkeypatch.setattr("app.releases.get_user_client", lambda token: client)

    from fastapi import HTTPException

    try:
        get_release("token", "missing")
        raise AssertionError("expected HTTPException")
    except HTTPException as exc:
        assert exc.status_code == 404
        assert exc.detail == "Component release not found"


def test_create_release_uses_trusted_admin_client(monkeypatch):
    client = MagicMock()
    client.table.return_value.insert.return_value.execute.return_value.data = [
        {"id": "release-1", "component": "agent", "version": "1.2.0"}
    ]
    monkeypatch.setattr("app.releases.get_admin_client", lambda: client)

    result = create_release(
        CreateReleaseRequest(
            component="agent",
            version="1.2.0",
            artifact_ref="release/agent-1.2.0.zip",
            checksum="abc123",
        )
    )

    assert result["id"] == "release-1"
    client.table.assert_called_once_with("component_releases")
