from fastapi import HTTPException

from app.supabase_client import get_admin_client, get_user_client, supabase


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
    """Look up a Telegram identity using the backend-only Supabase client.

    This endpoint is already protected by TELEGRAM_BOT_SHARED_SECRET. The
    lookup itself must not use the publishable/anon database role because
    profiles and children are protected by RLS.
    """
    try:
        admin_client = get_admin_client()

        profile_response = (
            admin_client
            .table("profiles")
            .select("id, display_name, telegram_id, role, is_active")
            .eq("telegram_id", telegram_id)
            .maybe_single()
            .execute()
        )

        if profile_response.data is not None:
            return {
                "type": "profile",
                **profile_response.data,
            }

        child_response = (
            admin_client
            .table("children")
            .select("id, family_id, name, avatar_url, telegram_id, is_active")
            .eq("telegram_id", telegram_id)
            .maybe_single()
            .execute()
        )

        if child_response.data is not None:
            return {
                "type": "child",
                **child_response.data,
            }

        return None

    except Exception as exc:
        print(f"TELEGRAM ID LOOKUP ERROR: {exc!r}")
        raise HTTPException(
            status_code=500,
            detail="Unable to lookup Telegram ID",
        ) from exc
