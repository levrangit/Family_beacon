import os
import time
import uuid

import pytest
from starlette.testclient import TestClient

from app.main import app


@pytest.mark.real_e2e
def test_real_registration_family_invite_redeem_flow(supabase_service_client):
    """Exercise the real Supabase-backed parent-to-parent flow.

    No auth, RPC, or invite-hash calls are mocked. Two temporary Supabase
    Auth users are registered through the real HTTP endpoint; the first
    creates a family and invite, and the second redeems the invite.

    Run explicitly with RUN_REAL_E2E=1 to avoid creating remote test users in
    normal unit-test runs.
    """
    if os.getenv("RUN_REAL_E2E") != "1":
        pytest.skip("set RUN_REAL_E2E=1 to run the real Supabase E2E flow")

    if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_KEY"):
        pytest.skip("SUPABASE_URL and SUPABASE_KEY are required")

    suffix = f"{int(time.time())}-{uuid.uuid4().hex[:8]}"
    parent1_email = f"e2e-parent1-{suffix}@example.com"
    parent2_email = f"e2e-parent2-{suffix}@example.com"
    password = "E2e-Test-Password-2026!"

    parent1_user_id = None
    parent2_user_id = None
    family_id = None
    invite_id = None

    try:
        with TestClient(app) as client:
            # 1. Real parent registration through the API.
        register1 = client.post(
            "/auth/register-parent",
            json={
                "telegram_id": int(f"1{int(time.time() * 1000) % 10**9:09d}"),
                "login": parent1_email,
                "password": password,
            },
        )
        assert register1.status_code == 200, register1.text
        parent1 = register1.json()
        assert parent1["user_id"]
        assert parent1["access_token"]

        parent1_user_id = parent1["user_id"]
        parent1_headers = {"Authorization": f"Bearer {parent1['access_token']}"}

        # 2. The first registered parent creates a real family via the DB RPC.
        create_family = client.post(
            "/families",
            json={"name": f"E2E Family {suffix}"},
            headers=parent1_headers,
        )
        assert create_family.status_code == 200, create_family.text
        family_id = create_family.json()["family_id"]
        assert family_id

        # 3. The first parent creates a real invite; hashing is not mocked.
        create_invite = client.post(
            f"/families/{family_id}/invite",
            headers=parent1_headers,
        )
        assert create_invite.status_code == 200, create_invite.text
        invite = create_invite.json()
        invite_id = invite["invite_id"]
        assert invite_id
        assert invite["family_id"] == family_id
        assert invite["code"]
        assert invite["expires_at"]

        # 4. Register a second real parent.
        register2 = client.post(
            "/auth/register-parent",
            json={
                "telegram_id": int(f"2{int(time.time() * 1000) % 10**9:09d}"),
                "login": parent2_email,
                "password": password,
            },
        )
        assert register2.status_code == 200, register2.text
        parent2 = register2.json()
        parent2_user_id = parent2["user_id"]
        assert parent2_user_id
        assert parent2["access_token"]
        assert parent2["user_id"] != parent1["user_id"]

        parent2_headers = {"Authorization": f"Bearer {parent2['access_token']}"}

        # 5. The second parent redeems the real invite.
        redeem = client.post(
            "/families/redeem-invite",
            json={"code": invite["code"]},
            headers=parent2_headers,
        )
        assert redeem.status_code == 200, redeem.text
        redeemed = redeem.json()
        assert redeemed == {
            "invite_id": invite["invite_id"],
            "family_id": family_id,
        }

        # 6. Verify the second parent can read the family through normal RLS.
        family = client.get(
            f"/families/{family_id}",
            headers=parent2_headers,
        )
        assert family.status_code == 200, family.text
        assert family.json()["id"] == family_id

    finally:
        if invite_id is not None:
            supabase_service_client.table("family_invites").delete().eq(
                "id", invite_id
            ).execute()
        if family_id is not None:
            supabase_service_client.table("families").delete().eq(
                "id", family_id
            ).execute()
        if parent2_user_id is not None:
            supabase_service_client.auth.admin.delete_user(parent2_user_id)
        if parent1_user_id is not None:
            supabase_service_client.auth.admin.delete_user(parent1_user_id)
