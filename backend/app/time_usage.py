from datetime import date

from fastapi import HTTPException
from pydantic import BaseModel

from app.supabase_client import get_user_client


class RecordTimeUsageRequest(BaseModel):
    child_id: str
    device_id: str | None = None
    usage_date: date
    additional_minutes: int


def record_time_usage(
    access_token: str,
    device_id: str | None = None,
    data: RecordTimeUsageRequest | None = None,
):
    if data is None:
        raise HTTPException(
            status_code=400,
            detail="Time usage data is required",
        )

    if data.additional_minutes < 0:
        raise HTTPException(
            status_code=400,
            detail="Usage minutes cannot be negative",
        )

    if not device_id:
        raise HTTPException(
            status_code=400,
            detail="Device ID is required",
        )

    try:
        client = get_user_client(access_token)

        response = client.rpc(
            "record_time_usage",
            {
                "target_child_id": data.child_id,
                "target_device_id": device_id,
                "target_usage_date": data.usage_date.isoformat(),
                "additional_minutes": data.additional_minutes,
            },
        ).execute()

        if not response.data:
            raise HTTPException(
                status_code=500,
                detail="Failed to record time usage",
            )

        return response.data

    except HTTPException:
        raise

    except Exception as exc:
        error_message = str(exc)

        if "Device not found" in error_message:
            raise HTTPException(
                status_code=404,
                detail="Device not found",
            )

        if "does not belong to child" in error_message:
            raise HTTPException(
                status_code=400,
                detail="Device does not belong to child",
            )

        if "Permission denied" in error_message:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to record time usage",
            )

        raise HTTPException(
            status_code=500,
            detail="Failed to record time usage",
        )


def list_time_usage(
    access_token: str,
    child_id: str | None = None,
    usage_date: date | None = None,
):
    try:
        client = get_user_client(access_token)

        query = client.table("time_usage").select(
            "id, child_id, device_id, usage_date, "
            "used_minutes, created_at, updated_at"
        )

        if child_id is not None:
            query = query.eq("child_id", child_id)

        if usage_date is not None:
            query = query.eq("usage_date", usage_date.isoformat())

        response = query.order("usage_date", desc=True).execute()

        return response.data or []

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to load time usage",
        )
