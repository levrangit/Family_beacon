from datetime import datetime, timedelta, timezone

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
