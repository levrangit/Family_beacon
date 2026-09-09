from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from app.main import app
from app.auth import get_current_user


def test_create_family_endpoint_returns_family_id():
    access_token = "test-access-token"

    app.dependency_overrides[get_current_user] = lambda: (
        MagicMock(id="parent-user-id"),
        access_token,
    )

    try:
        mock_user_client = MagicMock()

        rpc_response = MagicMock()
        rpc_response.data = "family-123"

        (
            mock_user_client
            .rpc.return_value
            .execute.return_value
        ) = rpc_response

        from app import main

        original_get_user_client = main.get_user_client
        main.get_user_client = lambda token: mock_user_client

        client = TestClient(app)

        response = client.post(
            "/families",
            json={"name": "My Family"},
        )

        assert response.status_code == 200
        assert response.json() == {
            "family_id": "family-123",
        }

        mock_user_client.rpc.assert_called_once_with(
            "create_family",
            {"family_name": "My Family"},
        )

    finally:
        main.get_user_client = original_get_user_client
        app.dependency_overrides.clear()
