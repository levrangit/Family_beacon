from fastapi import HTTPException

from app.supabase_client import get_user_client


DEVICE_UPDATE_NOT_FOUND = "Device update not found"


def list_device_updates(
    access_token: str,
    device_id: str,
):
    try:
        client = get_user_client(access_token)

        response = (
            client
            .table("device_updates")
            .select(
                "id, device_id, component, from_version, target_version, "
                "status, attempt, started_at, completed_at, error_code, "
                "error_message, rollback_version, created_at, updated_at"
            )
            .eq("device_id", device_id)
            .order("created_at", desc=True)
            .execute()
        )

        return response.data or []

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to load device update history",
        )


def get_device_update(
    access_token: str,
    device_id: str,
    update_id: str,
):
    try:
        client = get_user_client(access_token)

        response = (
            client
            .table("device_updates")
            .select(
                "id, device_id, component, from_version, target_version, "
                "status, attempt, started_at, completed_at, error_code, "
                "error_message, rollback_version, created_at, updated_at"
            )
            .eq("id", update_id)
            .eq("device_id", device_id)
            .maybe_single()
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=404,
                detail=DEVICE_UPDATE_NOT_FOUND,
            )

        return response.data

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to load device update",
        )
