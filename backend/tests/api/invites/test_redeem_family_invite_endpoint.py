from unittest.mock import MagicMock

from starlette.testclient import TestClient

from app.main import app
from app.auth import get_current_user
from app import family_invites


def test_redeem_family_invite_endpoint_returns_family_data():
    access_token = "test-access-token"

    app.dependency_overrides[get_current_user] = lambda: (
        MagicMock(id="child-user-id"),
        access_token,
    )

    try:
        mock_user_client = MagicMock()

        rpc_response = MagicMock()
        rpc_response.data = [
            {
                "invite_id": "invite-id",
                "family_id": "family-id",
            }
        ]

        (
            mock_user_client.rpc.return_value.execute.return_value
        ) = rpc_response

        from app import main

        original_get_user_client = main.get_user_client
        original_hash_invite_code = family_invites.hash_invite_code
        main.get_user_client = lambda token: mock_user_client
        family_invites.hash_invite_code = lambda code: "hashed-invite-code"

        with TestClient(app) as client:
            response = client.post(
                "/families/redeem-invite",
                json={"code": "7K4M-92QX"},
            )

        assert response.status_code == 200
        assert response.json() == {
            "invite_id": "invite-id",
            "family_id": "family-id",
        }

        mock_user_client.rpc.assert_called_once_with(
            "redeem_family_invite",
            {"p_code_hash": "hashed-invite-code"},
        )

    finally:
        main.get_user_client = original_get_user_client
        family_invites.hash_invite_code = original_hash_invite_code
        app.dependency_overrides.clear()


def test_redeem_family_invite_endpoint_rejects_empty_code():
    access_token = "test-access-token"

    app.dependency_overrides[get_current_user] = lambda: (
        MagicMock(id="child-user-id"),
        access_token,
    )

    try:
        with TestClient(app) as client:
            response = client.post(
                "/families/redeem-invite",
                json={"code": ""},
            )

        assert response.status_code == 400
        assert response.json()["detail"] == "Invite code is required"

    finally:
        app.dependency_overrides.clear()


def test_redeem_family_invite_endpoint_rejects_invalid_code():
    access_token = "test-access-token"

    app.dependency_overrides[get_current_user] = lambda: (
        MagicMock(id="child-user-id"),
        access_token,
    )

    try:
        from app import main

        original_redeem_family_invite = main.redeem_family_invite

        def fake_redeem_family_invite(client, code):
            raise ValueError(
                "Invite is invalid, expired, revoked, or already used"
            )

        main.redeem_family_invite = fake_redeem_family_invite

        with TestClient(app) as client:
            response = client.post(
                "/families/redeem-invite",
                json={"code": "INVALID-CODE"},
            )

        assert response.status_code == 400
        assert response.json()["detail"] == (
            "Invite is invalid, expired, revoked, or already used"
        )

    finally:
        main.redeem_family_invite = original_redeem_family_invite
        app.dependency_overrides.clear()


def test_redeem_family_invite_endpoint_rejects_used_code():
    access_token = "test-access-token"

    app.dependency_overrides[get_current_user] = lambda: (
        MagicMock(id="child-user-id"),
        access_token,
    )

    try:
        from app import main

        original_redeem_family_invite = main.redeem_family_invite

        def fake_redeem_family_invite(client, code):
            raise ValueError(
                "Invite is invalid, expired, revoked, or already used"
            )

        main.redeem_family_invite = fake_redeem_family_invite

        with TestClient(app) as client:
            response = client.post(
                "/families/redeem-invite",
                json={"code": "7K4M-92QX"},
            )

        assert response.status_code == 400
        assert response.json()["detail"] == (
            "Invite is invalid, expired, revoked, or already used"
        )

    finally:
        main.redeem_family_invite = original_redeem_family_invite
        app.dependency_overrides.clear()
