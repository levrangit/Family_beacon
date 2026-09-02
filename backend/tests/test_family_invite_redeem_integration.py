import os
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from dotenv import load_dotenv
from supabase import create_client

from app.family_invites import create_family_invite, redeem_family_invite


load_dotenv(Path(".env"))

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
FAMILY_ID = "a0b728c8-ff11-43f1-ad73-c184ec6926d6"


@pytest.fixture
def supabase_client(parent_supabase_client):
    return parent_supabase_client


def test_redeem_family_invite_integration(
    parent_supabase_client,
    invite_redeemer_supabase_client,
):
    created = create_family_invite(
        parent_supabase_client,
        FAMILY_ID,
    )

    redeemed = redeem_family_invite(
        invite_redeemer_supabase_client,
        created["code"],
    )

    assert redeemed["invite_id"] == created["invite_id"]
    assert redeemed["family_id"] == FAMILY_ID


def test_redeem_family_invite_cannot_be_used_twice(
    parent_supabase_client,
    invite_redeemer_supabase_client,
):
    created = create_family_invite(
        parent_supabase_client,
        FAMILY_ID,
    )

    first_redeem = redeem_family_invite(
        invite_redeemer_supabase_client,
        created["code"],
    )

    assert first_redeem["invite_id"] == created["invite_id"]

    with pytest.raises(Exception, match="invalid|expired|revoked|used"):
        redeem_family_invite(
            invite_redeemer_supabase_client,
            created["code"],
        )


def test_redeem_expired_family_invite_is_rejected(supabase_client):
    created = create_family_invite(
        supabase_client,
        FAMILY_ID,
    )

    expired_at = (
        datetime.now(timezone.utc) - timedelta(minutes=1)
    ).isoformat()

    supabase_client.table("family_invites").update(
        {"expires_at": expired_at}
    ).eq(
        "id",
        created["invite_id"],
    ).execute()

    with pytest.raises(Exception, match="invalid|expired|revoked|used"):
        redeem_family_invite(
            supabase_client,
            created["code"],
        )


def test_redeem_revoked_family_invite_is_rejected(supabase_client):
    created = create_family_invite(
        supabase_client,
        FAMILY_ID,
    )

    revoked_at = datetime.now(timezone.utc).isoformat()

    supabase_client.table("family_invites").update(
        {"revoked_at": revoked_at}
    ).eq(
        "id",
        created["invite_id"],
    ).execute()

    with pytest.raises(Exception, match="invalid|expired|revoked|used"):
        redeem_family_invite(
            supabase_client,
            created["code"],
        )
