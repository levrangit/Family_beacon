from unittest.mock import MagicMock

import pytest
from starlette.testclient import TestClient

from app.auth import get_current_user
from app.family_invites import create_family_invite
from app.main import app


@pytest.mark.integration
def test_redeem_family_invite_endpoint_cannot_redeem_code_twice(
    parent_supabase_client,
    parent_family_id,
    invite_redeemer_supabase_client,
    supabase_service_client,
):
    created = create_family_invite(
        parent_supabase_client,
        parent_family_id,
    )

    app.dependency_overrides[get_current_user] = lambda: (
        MagicMock(id="invite-redeemer-user-id"),
        invite_redeemer_supabase_client.test_access_token,
    )

    try:
        import app.main as main

        original_get_user_client = main.get_user_client
        main.get_user_client = lambda token: invite_redeemer_supabase_client

        with TestClient(app) as client:
            first_response = client.post(
                "/families/redeem-invite",
                json={"code": created["code"]},
            )

            assert first_response.status_code == 200
            assert first_response.json()["invite_id"] == created["invite_id"]
            assert first_response.json()["family_id"] == parent_family_id

            second_response = client.post(
                "/families/redeem-invite",
                json={"code": created["code"]},
            )

            assert second_response.status_code == 400
            assert second_response.json()["detail"] == (
                "Invite is invalid, expired, revoked, or already used"
            )

    finally:
        main.get_user_client = original_get_user_client
        app.dependency_overrides.clear()
        supabase_service_client.table("family_invites").delete().eq(
            "id", created["invite_id"]
        ).execute()
