import os
import uuid

import pytest
import requests

from app.config import SUPABASE_KEY, SUPABASE_URL
from tests_backend.support.auth.temporary_users import cleanup_resources


@pytest.mark.integration
def test_full_parent_invite_flow(supabase_service_client, parent_access_token):
    """Exercise registration -> family -> invite -> transfer -> redeem through real services."""
    api_url = os.getenv("FAMILY_BEACON_API_URL", "http://127.0.0.1:8000")
    second_parent_password = f"Test-{uuid.uuid4().hex}-Aa1!"
    telegram_bot_shared_secret = os.getenv("TELEGRAM_BOT_SHARED_SECRET")

    if not telegram_bot_shared_secret:
        pytest.fail("TELEGRAM_BOT_SHARED_SECRET is required for the integration test")

    if not SUPABASE_URL or not SUPABASE_KEY:
        pytest.fail("Supabase configuration is required for the integration test")

    api = requests.Session()
    api.headers.update({"Authorization": f"Bearer {parent_access_token}"})

    family_id = None
    invite_id = None
    second_parent_user_id = None
    second_api = None

    family_name = f"integration-family-{uuid.uuid4()}"
    try:
        family_response = api.post(
            f"{api_url}/families",
            json={"name": family_name},
            timeout=10,
        )
        assert family_response.status_code == 200, family_response.text
        family_id = family_response.json()["family_id"]
        assert family_id

        invite_response = api.post(
            f"{api_url}/families/{family_id}/invite",
            timeout=10,
        )
        assert invite_response.status_code == 200, invite_response.text
        invite = invite_response.json()
        invite_id = invite["invite_id"]
        assert invite["family_id"] == str(family_id)
        assert invite["code"]
        assert invite_id

        second_parent_email = f"family-beacon-integration-{uuid.uuid4().hex}@example.com"
        registration_response = requests.post(
            f"{api_url}/auth/register-parent",
            headers={"X-Telegram-Bot-Key": telegram_bot_shared_secret},
            json={
                "telegram_id": int(uuid.uuid4().int % 2_000_000_000),
                "login": second_parent_email,
                "password": second_parent_password,
            },
            timeout=10,
        )

        if registration_response.status_code == 503:
            pytest.fail(registration_response.text)
        if registration_response.status_code != 200:
            pytest.fail(registration_response.text)

        registration = registration_response.json()
        second_parent_user_id = registration["user_id"]
        assert second_parent_user_id
        assert registration["access_token"]

        second_api = requests.Session()
        second_api.headers.update(
            {"Authorization": f"Bearer {registration['access_token']}"}
        )

        redeem_response = second_api.post(
            f"{api_url}/families/redeem-invite",
            json={"code": invite["code"]},
            timeout=10,
        )
        assert redeem_response.status_code == 200, redeem_response.text
        redeemed = redeem_response.json()
        assert redeemed["invite_id"] == invite_id
        assert redeemed["family_id"] == str(family_id)
    finally:
        cleanup_resources(
            (
                "family invite",
                lambda: supabase_service_client.table("family_invites")
                .delete()
                .eq("id", invite_id)
                .execute()
                if invite_id is not None
                else None,
            ),
            (
                "family",
                lambda: supabase_service_client.table("families")
                .delete()
                .eq("id", family_id)
                .execute()
                if family_id is not None
                else None,
            ),
            (
                "second parent Auth user",
                lambda: supabase_service_client.auth.admin.delete_user(
                    second_parent_user_id
                )
                if second_parent_user_id is not None
                else None,
            ),
            (
                "second parent HTTP client",
                lambda: second_api.close() if second_api is not None else None,
            ),
            ("parent HTTP client", api.close),
        )
