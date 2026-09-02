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

    original_redeem_family_invite = family_invites.redeem_family_invite

    try:
        family_invites.redeem_family_invite = lambda client, code: {
            "invite_id": "invite-1",
            "family_id": "family-1",
        }

        client = TestClient(app)
        response = client.post(
            "/families/redeem-invite",
            json={"code": "ABC123"},
        )

        assert response.status_code == 200
        assert response.json() == {
            "invite_id": "invite-1",
            "family_id": "family-1",
        }
    finally:
        family_invites.redeem_family_invite = original_redeem_family_invite
        app.dependency_overrides.clear()


def test_redeem_family_invite_endpoint_returns_400_for_invalid_code():
    access_token = "test-access-token"

    app.dependency_overrides[get_current_user] = lambda: (
        MagicMock(id="child-user-id"),
        access_token,
    )

    original_redeem_family_invite = family_invites.redeem_family_invite

    try:
        def reject_invite(client, code):
            raise ValueError(
                "Invite is invalid, expired, revoked, or already used"
            )

        family_invites.redeem_family_invite = reject_invite

        client = TestClient(app)
        response = client.post(
            "/families/redeem-invite",
            json={"code": "INVALID"},
        )

        assert response.status_code == 400
        assert response.json()["detail"] == (
            "Invite is invalid, expired, revoked, or already used"
        )
    finally:
        family_invites.redeem_family_invite = original_redeem_family_invite
        app.dependency_overrides.clear()


def test_redeem_family_invite_endpoint_cannot_redeem_code_twice(
    parent_supabase_client,
    invite_redeemer_supabase_client,
):
    from app import main
    from app.family_invites import create_family_invite

    family_id = "a0b728c8-ff11-43f1-ad73-c184ec6926d6"

    created = create_family_invite(
        parent_supabase_client,
        family_id,
    )

    app.dependency_overrides[get_current_user] = lambda: (
        MagicMock(id="invite-redeemer-user-id"),
        invite_redeemer_supabase_client.postgrest.session.headers["Authorization"].removeprefix("Bearer "),
    )

    try:
        original_get_user_client = main.get_user_client

        main.get_user_client = lambda token: invite_redeemer_supabase_client

        with TestClient(app) as client:
            first_response = client.post(
                "/families/redeem-invite",
                json={"code": created["code"]},
            )

            assert first_response.status_code == 200
            assert first_response.json()["invite_id"] == created["invite_id"]
            assert first_response.json()["family_id"] == family_id

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
