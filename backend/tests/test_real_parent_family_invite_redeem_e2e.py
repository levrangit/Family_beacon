import os
import time
import uuid

import pytest
from fastapi.testclient import TestClient

from app.auth import get_current_user
from app.main import app


@pytest.mark.real_e2e
def test_real_registration_family_invite_redeem_flow():
    """Exercise the real Supabase-backed parent-to-parent flow.

    The test intentionally does not mock auth, RPCs, or invite hashing.
    It creates two temporary Supabase Auth users, registers both through the
    HTTP endpoint, creates a family with the first parent, creates an invite,
    and redeems that invite with the second parent's access token.

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

    client = TestClient(app)

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

    # 2. The first registered parent creates a real family via the DB RPC.
    app.dependency_overrides[get_current_user] = lambda: (None, parent1["access_token"])
    try:
        create_family = client.post(
            "/families",
            json={"name": f"E2E Family {suffix}"},
        )
    finally:
        app.dependency_overrides.clear()

    assert create_family.status_code == 200, create_family.text
    family_id = create_family.json()["family_id"]
    assert family_id

    # 3. The first parent creates a real invite; hashing is not mocked.
    app.dependency_overrides[get_current_user] = lambda: (None, parent1["access_token"])
    try:
        create_invite = client.post(f"/families/{family_id}/invite")
    finally:
        app.dependency_overrides.clear()

    assert create_invite.status_code == 200, create_invite.text
    invite = create_invite.json()
    assert invite["invite_id"]
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
    assert parent2["user_id"]
    assert parent2["access_token"]
    assert parent2["user_id"] != parent1["user_id"]

    # 5. The second parent redeems the real invite.
    app.dependency_overrides[get_current_user] = lambda: (None, parent2["access_token"])
    try:
        redeem = client.post(
            "/families/redeem-invite",
            json={"code": invite["code"]},
        )
    finally:
        app.dependency_overrides.clear()

    assert redeem.status_code == 200, redeem.text
    redeemed = redeem.json()
    assert redeemed == {
        "invite_id": invite["invite_id"],
        "family_id": family_id,
    }

    # 6. Verify the second parent can read the family through normal RLS.
    app.dependency_overrides[get_current_user] = lambda: (None, parent2["access_token"])
    try:
        family = client.get(f"/families/{family_id}")
    finally:
        app.dependency_overrides.clear()

    assert family.status_code == 200, family.text
    assert family.json()["id"] == family_id
