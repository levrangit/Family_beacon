from datetime import time

from fastapi import HTTPException
from pydantic import BaseModel, Field

from app.supabase_client import get_user_client


RLS_ERROR_MARKER = "row-level security policy"
TIME_POLICY_NOT_FOUND = "Time policy not found"


class CreateTimePolicyRequest(BaseModel):
    child_id: str
    day_of_week: int = Field(ge=0, le=6)
    daily_limit_minutes: int = Field(ge=0)
    start_time: time | None = None
    end_time: time | None = None
    is_enabled: bool = True


class UpdateTimePolicyRequest(BaseModel):
    day_of_week: int | None = Field(default=None, ge=0, le=6)
    daily_limit_minutes: int | None = Field(default=None, ge=0)
    start_time: time | None = None
    end_time: time | None = None
    is_enabled: bool | None = None


def list_time_policies(
    access_token: str,
    child_id: str,
):
    try:
        client = get_user_client(access_token)

        response = (
            client
            .table("time_policies")
            .select(
                "id, child_id, day_of_week, daily_limit_minutes, "
                "start_time, end_time, is_enabled, "
                "created_at, updated_at"
            )
            .eq("child_id", child_id)
            .order("day_of_week")
            .execute()
        )

        return response.data or []

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to load time policies",
        )


def get_time_policy(
    access_token: str,
    policy_id: str,
):
    try:
        client = get_user_client(access_token)

        response = (
            client
            .table("time_policies")
            .select(
                "id, child_id, day_of_week, daily_limit_minutes, "
                "start_time, end_time, is_enabled, "
                "created_at, updated_at"
            )
            .eq("id", policy_id)
            .execute()
        )

        policies = response.data or []

        if not policies:
            raise HTTPException(
                status_code=404,
                detail=TIME_POLICY_NOT_FOUND,
            )

        return policies[0]

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to load time policy",
        )


def create_time_policy(
    access_token: str,
    data: CreateTimePolicyRequest,
):
    try:
        client = get_user_client(access_token)

        response = (
            client
            .table("time_policies")
            .insert(
                {
                    "child_id": data.child_id,
                    "day_of_week": data.day_of_week,
                    "daily_limit_minutes": data.daily_limit_minutes,
                    "start_time": (
                        data.start_time.isoformat()
                        if data.start_time
                        else None
                    ),
                    "end_time": (
                        data.end_time.isoformat()
                        if data.end_time
                        else None
                    ),
                    "is_enabled": data.is_enabled,
                }
            )
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=500,
                detail="Failed to create time policy",
            )

        return response.data[0]

    except HTTPException:
        raise

    except Exception as exc:
        error_message = str(exc)

        if RLS_ERROR_MARKER in error_message:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to create this time policy",
            )

        if "duplicate key" in error_message:
            raise HTTPException(
                status_code=409,
                detail="Time policy for this day already exists",
            )

        raise HTTPException(
            status_code=500,
            detail="Failed to create time policy",
        )


def update_time_policy(
    access_token: str,
    policy_id: str,
    data: UpdateTimePolicyRequest,
):
    try:
        client = get_user_client(access_token)

        updates = data.model_dump(
            exclude_unset=True,
            exclude_none=True,
        )

        for field in ("start_time", "end_time"):
            if field in updates:
                updates[field] = updates[field].isoformat()

        if not updates:
            raise HTTPException(
                status_code=400,
                detail="No fields to update",
            )

        response = (
            client
            .table("time_policies")
            .update(updates)
            .eq("id", policy_id)
            .execute()
        )

        policies = response.data or []

        if not policies:
            raise HTTPException(
                status_code=404,
                detail=TIME_POLICY_NOT_FOUND,
            )

        return policies[0]

    except HTTPException:
        raise

    except Exception as exc:
        error_message = str(exc)

        if RLS_ERROR_MARKER in error_message:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to update this time policy",
            )

        if "duplicate key" in error_message:
            raise HTTPException(
                status_code=409,
                detail="Time policy for this day already exists",
            )

        raise HTTPException(
            status_code=500,
            detail="Failed to update time policy",
        )


def delete_time_policy(
    access_token: str,
    policy_id: str,
):
    try:
        client = get_user_client(access_token)

        response = (
            client
            .table("time_policies")
            .delete()
            .eq("id", policy_id)
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=404,
                detail=TIME_POLICY_NOT_FOUND,
            )

        return {
            "deleted": True,
            "policy_id": policy_id,
        }

    except HTTPException:
        raise

    except Exception as exc:
        error_message = str(exc)

        if RLS_ERROR_MARKER in error_message:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to delete this time policy",
            )

        raise HTTPException(
            status_code=500,
            detail="Failed to delete time policy",
        )
