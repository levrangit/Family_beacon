from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app import family_invites
from app.auth import get_current_user
from app.main import app


def test_new_parent_can_redeem_invite_after_registration_contract():
    access_token = "new-parent-access-token"
    app.dependency_overrides[get_current_user] = lambda: (
        MagicMock(id="new-parent-user-id"),
        access_token,
    )

    mock_user_client = MagicMock()
    rpc_response = MagicMock()
    rpc_response.data = [{"invite_id": "invite-123", "family_id": "family-123"}]
    mock_user_client.rpc.return_value.execute.return_value = rpc_response

    from app import main

    original_get_user_client = main.get_user_client
    main.get_user_client = lambda token: mock_user_client

    try:
        with patch.object(
            family_invites,
            "hash_invite_code",
            return_value="hashed-invite-code",
        ) as mock_hash:
            client = TestClient(app)
            response = client.post(
                "/families/redeem-invite",
                json={"code": "7K4M-92QX"},
            )

            assert response.status_code == 200
            assert response.json() == {
                "invite_id": "invite-123",
                "family_id": "family-123",
            }
            mock_user_client.rpc.assert_called_once_with(
                "redeem_family_invite",
                {"p_code_hash": "hashed-invite-code"},
            )
            mock_hash.assert_called_once_with("7K4M-92QX")
    finally:
        main.get_user_client = original_get_user_client
        app.dependency_overrides.clear()
