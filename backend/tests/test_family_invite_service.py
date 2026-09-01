from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

import pytest

from app.family_invites import create_family_invite


def test_create_family_invite_calls_rpc_with_family_id_and_code_hash():
    client = MagicMock()

    response = MagicMock()
    response.data = [{
        "id": "invite-123",
        "family_id": "family-123",
        "expires_at": "2026-09-02T12:00:00+00:00",
    }]

    client.rpc.return_value.execute.return_value = response

    result = create_family_invite(
        supabase_client=client,
        family_id="family-123",
    )

    assert result["invite_id"] == "invite-123"
    assert result["family_id"] == "family-123"
    assert "code" in result
    assert "code_hash" not in result

    client.rpc.assert_called_once()

    rpc_name, rpc_params = client.rpc.call_args.args

    assert rpc_name == "create_family_invite"
    assert rpc_params["p_family_id"] == "family-123"
    assert len(rpc_params["p_code_hash"]) == 64
    assert rpc_params["p_expires_at"]


def test_create_family_invite_uses_24_hour_expiration():
    client = MagicMock()

    response = MagicMock()
    response.data = [{
        "id": "invite-123",
        "family_id": "family-123",
        "expires_at": "2026-09-02T12:00:00+00:00",
    }]

    client.rpc.return_value.execute.return_value = response

    before = datetime.now(timezone.utc)

    create_family_invite(
        supabase_client=client,
        family_id="family-123",
    )

    after = datetime.now(timezone.utc)

    _, rpc_params = client.rpc.call_args.args

    expires_at = datetime.fromisoformat(rpc_params["p_expires_at"])

    assert before + timedelta(hours=24) <= expires_at <= after + timedelta(hours=24)


def test_create_family_invite_rejects_empty_family_id():
    client = MagicMock()

    with pytest.raises(ValueError, match="Family ID is required"):
        create_family_invite(
            supabase_client=client,
            family_id="",
        )

    client.rpc.assert_not_called()


def test_create_family_invite_rejects_missing_rpc_result():
    client = MagicMock()

    response = MagicMock()
    response.data = None

    client.rpc.return_value.execute.return_value = response

    with pytest.raises(
        ValueError,
        match="Invite ID was not returned",
    ):
        create_family_invite(
            supabase_client=client,
            family_id="family-123",
        )
