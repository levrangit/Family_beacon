from fastapi import Header, HTTPException

from app.device_auth import get_device_token_hash
from app.supabase_client import supabase


def device_heartbeat(
    authorization: str | None = Header(default=None),
):
    token_hash = get_device_token_hash(authorization)

    if supabase is None:
        raise HTTPException(
            status_code=500,
            detail="Supabase configuration is missing",
        )

    try:
        response = (
            supabase
            .rpc(
                "device_heartbeat_by_token",
                {
                    "target_token_hash": token_hash,
                },
            )
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=401,
                detail="Invalid device token",
            )

        return response.data

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Device heartbeat failed",
        )
