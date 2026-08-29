from fastapi import HTTPException
from pydantic import BaseModel

from app.supabase_client import get_user_client

class CreateChildRequest(BaseModel):
    name: str
    avatar_url: str | None = None

def create_child(
    access_token: str,
    family_id: str,
    data: CreateChildRequest,
):
    try:
        client = get_user_client(access_token)

        response = (
            client
            .table("children")
            .insert(
                {
                    "family_id": family_id,
                    "name": data.name,
                    "avatar_url": data.avatar_url,
                }
            )
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=500,
                detail="Failed to create child",
            )

        return response.data[0]

    except HTTPException:
        raise

    except Exception as exc:
        error_message = str(exc)

        if "row-level security policy" in error_message:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to create a child in this family",
            )

        raise HTTPException(
            status_code=500,
            detail="Failed to create child",
        )


def list_children(
    access_token: str,
    family_id: str,
):
    try:
        client = get_user_client(access_token)

        response = (
            client
            .table("children")
            .select(
                "id, family_id, name, avatar_url, is_active, "
                "created_at, updated_at"
            )
            .eq("family_id", family_id)
            .order("created_at")
            .execute()
        )

        return response.data or []

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to load children",
        )
