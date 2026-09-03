from fastapi import HTTPException

from app.config import TELEGRAM_BOT_SHARED_SECRET
from app.supabase_client import get_user_client, supabase


def get_profile(user_id: str, access_token: str):
    try:
        user_client = get_user_client(access_token)

        response = (
            user_client
            .table("profiles")
            .select("id, display_name, telegram_id, role, is_active")
            .eq("id", user_id)
            .maybe_single()
            .execute()
        )

        if response.data is None:
            raise HTTPException(
                status_code=404,
                detail="Profile not found",
            )

        return response.data

    except HTTPException:
        raise

    except Exception as exc:
        print(f"PROFILE ERROR: {exc!r}")
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


def lookup_profile_by_telegram_id(telegram_id: int):
    if supabase is None:
        raise HTTPException(
            status_code=503,
            detail="Supabase configuration is missing",
        )

    try:
        response = (
            supabase
            .table("profiles")
            .select("id, display_name, telegram_id, role, is_active")
            .eq("telegram_id", telegram_id)
            .maybe_single()
            .execute()
        )

        return response.data

    except Exception as exc:
        print(f"TELEGRAM PROFILE LOOKUP ERROR: {exc!r}")
        raise HTTPException(
            status_code=500,
            detail="Unable to lookup Telegram ID",
        ) from exc
