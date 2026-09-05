from datetime import date

from fastapi import HTTPException
from pydantic import BaseModel

from app.supabase_client import get_user_client, supabase_admin


class RecordTimeUsageRequest(BaseModel):
    child_id: str
    device_id: str
    usage_date: date
    additional_minutes: int


class DeviceRecordTimeUsageRequest(BaseModel):
    child_id: str
    usage_date: date
    additional_minutes: int


def record_time_usage(
    access_token: str,
    device_id: str,
    data: RecordTimeUsageRequest,
):
    if data.additional_minutes < 0:
        raise HTTPException(
            status_code=400,
            detail="Usage minutes cannot be negative",
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


def record_time_usage_for_device(
    device_id: str,
    data: DeviceRecordTimeUsageRequest,
):
    if data.additional_minutes < 0:
        raise HTTPException(
            status_code=400,
            detail="Usage minutes cannot be negative",
        )

    if supabase_admin is None:
        raise HTTPException(
            status_code=500,
            detail="Supabase service role configuration is missing",
        )

    try:
        device_response = (
            supabase_admin
            .table("devices")
            .select("id, child_id")
            .eq("id", device_id)
            .execute()
        )

        devices = device_response.data or []

        if not devices:
            raise HTTPException(
                status_code=404,
                detail="Device not found",
            )

        device = devices[0]

        if device.get("child_id") != data.child_id:
            raise HTTPException(
                status_code=400,
                detail="Device does not belong to child",
            )

        response = (
            supabase_admin
            .table("time_usage")
            .upsert(
                {
                    "child_id": data.child_id,
                    "device_id": device_id,
                    "usage_date": data.usage_date.isoformat(),
                    "used_minutes": data.additional_minutes,
                },
                on_conflict="child_id,device_id,usage_date",
            )
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=500,
                detail="Failed to record time usage",
            )

        return response.data[0]

    except HTTPException:
        raise

    except Exception:
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
