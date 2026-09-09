from unittest.mock import MagicMock

from app.compatibility import CreateCompatibilityRequest, create_compatibility, list_compatibility


def test_list_compatibility_returns_rules(monkeypatch):
    client = MagicMock()
    client.table.return_value.select.return_value.order.return_value.execute.return_value.data = [
        {"id": "compat-1", "release_id": "release-1", "platform": "windows"}
    ]
    monkeypatch.setattr("app.compatibility.get_user_client", lambda token: client)

    result = list_compatibility("token")

    assert result == [
        {"id": "compat-1", "release_id": "release-1", "platform": "windows"}
    ]
    client.table.assert_called_once_with("component_compatibility")


def test_create_compatibility_uses_trusted_admin_client(monkeypatch):
    client = MagicMock()
    client.table.return_value.insert.return_value.execute.return_value.data = [
        {"id": "compat-1", "release_id": "release-1", "platform": "windows"}
    ]
    monkeypatch.setattr("app.compatibility.get_admin_client", lambda: client)

    result = create_compatibility(
        CreateCompatibilityRequest(
            release_id="release-1",
            platform="windows",
            min_agent_version="1.0.0",
            max_agent_version="2.0.0",
        )
    )

    assert result["id"] == "compat-1"
    client.table.assert_called_once_with("component_compatibility")
