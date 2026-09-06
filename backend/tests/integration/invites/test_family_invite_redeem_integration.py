from datetime import datetime, timedelta, timezone

import pytest

from app.family_invites import create_family_invite, redeem_family_invite


@pytest.fixture
def supabase_client(parent_supabase_client):
    return parent_supabase_client


def test_redeem_family_invite_integration(
    parent_supabase_client,
    parent_family_id,
    invite_redeemer_supabase_client,
    supabase_service_client,
):
    created = create_family_invite(
        parent_supabase_client,
        parent_family_id,
    )

    try:
        redeemed = redeem_family_invite(
            invite_redeemer_supabase_client,
            created["code"],
        )

        assert redeemed["invite_id"] == created["invite_id"]
        assert redeemed["family_id"] == parent_family_id
    finally:
        supabase_service_client.table("family_invites").delete().eq(
            "id", created["invite_id"]
        ).execute()


def test_redeem_family_invite_cannot_be_used_twice(
    parent_supabase_client,
    parent_family_id,
    invite_redeemer_supabase_client,
    supabase_service_client,
):
    created = create_family_invite(
        parent_supabase_client,
        parent_family_id,
    )

    try:
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
    finally:
        supabase_service_client.table("family_invites").delete().eq(
            "id", created["invite_id"]
        ).execute()


def test_redeem_expired_family_invite_is_rejected(
    supabase_client,
    parent_family_id,
    supabase_service_client,
):
    created = create_family_invite(
        supabase_client,
        parent_family_id,
    )

    try:
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
    finally:
        supabase_service_client.table("family_invites").delete().eq(
            "id", created["invite_id"]
        ).execute()


def test_redeem_revoked_family_invite_is_rejected(
    supabase_client,
    parent_family_id,
    supabase_service_client,
):
    created = create_family_invite(
        supabase_client,
        parent_family_id,
    )

    try:
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
    finally:
        supabase_service_client.table("family_invites").delete().eq(
            "id", created["invite_id"]
        ).execute()
