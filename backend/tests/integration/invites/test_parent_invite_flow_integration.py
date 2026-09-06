import os
import uuid

import pytest
import requests
from supabase import create_client

from app.config import SUPABASE_KEY, SUPABASE_URL


@pytest.mark.integration
def test_full_parent_invite_flow(supabase_service_client):
    """Exercise registration -> family -> invite -> transfer -> redeem through real services."""
    api_url = os.getenv("FAMILY_BEACON_API_URL", "http://127.0.0.1:8000")
    first_parent_email = os.getenv("TEST_PARENT_EMAIL") or os.getenv("TEST_EMAIL")
    first_parent_password = os.getenv("TEST_PARENT_PASSWORD") or os.getenv("TEST_PASSWORD")
    second_parent_password = os.getenv("TEST_SECOND_PARENT_PASSWORD")

    if not first_parent_email or not first_parent_password or not second_parent_password:
        pytest.fail(
            "TEST_PARENT_EMAIL, TEST_PARENT_PASSWORD and "
            "TEST_SECOND_PARENT_PASSWORD are required for the integration test"
        )

    if not SUPABASE_URL or not SUPABASE_KEY:
        pytest.fail("Supabase configuration is required for the integration test")

    first_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    first_auth = first_client.auth.sign_in_with_password(
        {"email": first_parent_email, "password": first_parent_password}
    )
    assert first_auth.session is not None
    first_token = first_auth.session.access_token

    api = requests.Session()
    api.headers.update({"Authorization": f"Bearer {first_token}"})

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
        if invite_id is not None:
            supabase_service_client.table("family_invites").delete().eq(
                "id", invite_id
            ).execute()
        if family_id is not None:
            supabase_service_client.table("families").delete().eq(
                "id", family_id
            ).execute()
        if second_parent_user_id is not None:
            supabase_service_client.auth.admin.delete_user(second_parent_user_id)
        if second_api is not None:
            second_api.close()
        api.close()
