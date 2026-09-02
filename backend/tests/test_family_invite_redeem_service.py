from unittest.mock import Mock

import pytest
from unittest.mock import MagicMock

from app.family_invites import redeem_family_invite


from postgrest.exceptions import APIError
def test_redeem_family_invite_returns_invite_and_family():
    client = Mock()
    client.rpc.return_value.execute.return_value.data = [
        {
            "invite_id": "11111111-1111-1111-1111-111111111111",
            "family_id": "22222222-2222-2222-2222-222222222222",
        }
    ]

    result = redeem_family_invite(client, "ABCD-2345")

    assert result == {
        "invite_id": "11111111-1111-1111-1111-111111111111",
        "family_id": "22222222-2222-2222-2222-222222222222",
    }

    client.rpc.assert_called_once()


def test_redeem_family_invite_rejects_empty_code():
    client = Mock()

    with pytest.raises(ValueError, match="Invite code is required"):
        redeem_family_invite(client, "")


def test_redeem_family_invite_rejects_missing_response():
    client = Mock()
    client.rpc.return_value.execute.return_value.data = None

    with pytest.raises(
        ValueError,
        match="Invite could not be redeemed",
    ):
        redeem_family_invite(client, "ABCD-2345")


def test_redeem_family_invite_translates_invalid_invite_api_error():
    client = MagicMock()

    api_error = APIError(
        {
            "message": "Invite is invalid, expired, revoked, or already used",
            "code": "P0001",
            "hint": None,
            "details": None,
        }
    )

    client.rpc.return_value.execute.side_effect = api_error

    with pytest.raises(
        ValueError,
        match="Invite is invalid, expired, revoked, or already used",
    ):
        redeem_family_invite(client, "INVALID-CODE")
