from fastapi import HTTPException

from app.supabase_client import get_user_client


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
