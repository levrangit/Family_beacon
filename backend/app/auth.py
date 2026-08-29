from fastapi import Header, HTTPException

from app.supabase_client import supabase


async def get_current_user(
    authorization: str | None = Header(default=None),
):
    if supabase is None:
        raise HTTPException(
            status_code=500,
            detail="Supabase configuration is missing",
        )

    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header is required",
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Authorization header must use Bearer token",
        )

    token = authorization.removeprefix("Bearer ").strip()

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Bearer token is empty",
        )

    try:
        response = supabase.auth.get_user(token)

        if response.user is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication token",
            )

        return response.user, token

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token",
        )
