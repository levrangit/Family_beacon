from fastapi import HTTPException

from app.supabase_client import get_user_client


def list_families(access_token: str):
    try:
        client = get_user_client(access_token)

        response = (
            client
            .table("families")
            .select("id, name, created_at, updated_at")
            .order("created_at")
            .execute()
        )

        return response.data or []

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to load families",
        )


def get_family(
    access_token: str,
    family_id: str,
):
    try:
        client = get_user_client(access_token)

        family_response = (
            client
            .table("families")
            .select("id, name, created_at, updated_at")
            .eq("id", family_id)
            .execute()
        )

        families = family_response.data or []

        if not families:
            raise HTTPException(
                status_code=404,
                detail="Family not found",
            )

        family = families[0]

        children_response = (
            client
            .table("children")
            .select(
                "id, name, avatar_url, is_active, "
                "created_at, updated_at"
            )
            .eq("family_id", family_id)
            .order("created_at")
            .execute()
        )

        return {
            **family,
            "children": children_response.data or [],
        }

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to load family",
        )


def create_family(
    supabase_client,
    family_name: str,
):
    if not family_name.strip():
        raise ValueError("Family name is required")

    response = supabase_client.rpc(
        "create_family",
        {
            "family_name": family_name,
        },
    ).execute()

    if response.data is None:
        raise ValueError("Family ID was not returned")

    return response.data
