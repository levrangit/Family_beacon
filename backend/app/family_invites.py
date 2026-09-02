from datetime import datetime, timedelta, timezone

from postgrest.exceptions import APIError

from .invite_code import generate_invite_code, hash_invite_code


def create_family_invite(supabase_client, family_id: str) -> dict:
    if not family_id.strip():
        raise ValueError("Family ID is required")

    code = generate_invite_code()
    code_hash = hash_invite_code(code)

    expires_at = (
        datetime.now(timezone.utc) + timedelta(hours=24)
    ).isoformat()

    response = supabase_client.rpc(
        "create_family_invite",
        {
            "p_family_id": family_id,
            "p_code_hash": code_hash,
            "p_expires_at": expires_at,
        },
    ).execute()

    if not response.data:
        raise ValueError("Invite ID was not returned")

    invite = response.data[0]

    return {
        "invite_id": str(invite["id"]),
        "family_id": str(invite["family_id"]),
        "code": code,
        "expires_at": str(invite["expires_at"]),
    }


def redeem_family_invite(supabase_client, code: str) -> dict:
    if not code.strip():
        raise ValueError("Invite code is required")

    code_hash = hash_invite_code(code)

    try:
        response = supabase_client.rpc(
            "redeem_family_invite",
            {
                "p_code_hash": code_hash,
            },
        ).execute()
    except APIError as exc:
        if getattr(exc, "code", None) == "P0001":
            message = getattr(
                exc,
                "message",
                "Invite is invalid, expired, revoked, or already used",
            )
            raise ValueError(message) from exc
        raise

    if response.data is None:
        raise ValueError("Invite could not be redeemed")

    data = response.data[0] if isinstance(response.data, list) else response.data

    return {
        "invite_id": str(data["invite_id"]),
        "family_id": str(data["family_id"]),
    }
