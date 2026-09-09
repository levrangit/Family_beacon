from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.auth import get_current_user
from app.main import app


def test_create_family_invite_endpoint_returns_invite_code():
    access_token = "parent-access-token"
    app.dependency_overrides[get_current_user] = lambda: (
        MagicMock(id="parent-user-id"),
        access_token,
    )

    mock_user_client = MagicMock()
    rpc_response = MagicMock()
    rpc_response.data = [
        {
            "id": "invite-123",
            "family_id": "family-123",
            "expires_at": "2026-09-03T12:00:00+00:00",
        }
    ]
    mock_user_client.rpc.return_value.execute.return_value = rpc_response

    from app import main
    from app import family_invites

    original_get_user_client = main.get_user_client
    original_generate_invite_code = family_invites.generate_invite_code
    original_hash_invite_code = family_invites.hash_invite_code
    main.get_user_client = lambda token: mock_user_client
    family_invites.generate_invite_code = lambda: "7K4M-92QX"
    family_invites.hash_invite_code = lambda code: "hashed-invite-code"

    try:
        client = TestClient(app)
        response = client.post("/families/family-123/invite")

        assert response.status_code == 200
        assert response.json() == {
            "invite_id": "invite-123",
            "family_id": "family-123",
            "code": "7K4M-92QX",
            "expires_at": "2026-09-03T12:00:00+00:00",
        }
        mock_user_client.rpc.assert_called_once()
        assert mock_user_client.rpc.call_args.args[0] == "create_family_invite"
        assert mock_user_client.rpc.call_args.args[1]["p_family_id"] == "family-123"
        assert mock_user_client.rpc.call_args.args[1]["p_code_hash"] == "hashed-invite-code"
    finally:
        main.get_user_client = original_get_user_client
        family_invites.generate_invite_code = original_generate_invite_code
        family_invites.hash_invite_code = original_hash_invite_code
        app.dependency_overrides.clear()


def test_create_family_invite_endpoint_delegates_to_create_family_invite_service():
    from app import main

    access_token = "parent-access-token"
    app.dependency_overrides[get_current_user] = lambda: (
        MagicMock(id="parent-user-id"),
        access_token,
    )
    mock_user_client = MagicMock()
    original_get_user_client = main.get_user_client
    main.get_user_client = lambda token: mock_user_client
    expected = {
        "invite_id": "invite-123",
        "family_id": "family-123",
        "code": "7K4M-92QX",
        "expires_at": "2026-09-03T12:00:00+00:00",
    }

    try:
        with patch.object(
            main,
            "create_family_invite",
            return_value=expected,
        ) as mock_create_invite:
            response = TestClient(app).post("/families/family-123/invite")

        assert response.status_code == 200
        assert response.json() == expected
        mock_create_invite.assert_called_once_with(
            mock_user_client,
            "family-123",
        )
    finally:
        main.get_user_client = original_get_user_client
        app.dependency_overrides.clear()
