
from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel

from app.auth import get_current_user
from app.children import (
    CreateChildRequest,
    create_child,
    list_children,
)
from app.devices import (
    CreateDeviceRequest,
    UpdateDeviceRequest,
    create_device,
    list_devices,
    get_device,
    update_device,
    delete_device,
    heartbeat_device,
)
from app.time_policies import (
    CreateTimePolicyRequest,
    UpdateTimePolicyRequest,
    create_time_policy,
    list_time_policies,
    get_time_policy,
    update_time_policy,
    delete_time_policy,
)
from app.families import get_family, list_families
from app.family_invites import redeem_family_invite
from app.time_usage import (
    RecordTimeUsageRequest,
    record_time_usage,
    list_time_usage,
)
from app.profiles import get_profile
from app.supabase_client import get_user_client, supabase

from app.commands import (
    CreateCommandRequest,
    create_command,
    list_commands,
    get_command,
)

from app.device_agent import device_heartbeat

from app.device_auth import (
    DeviceAuthRequest,
    authenticate_device,
    create_device_auth_token,
    claim_next_device_command,
    complete_device_command,
    recover_stale_device_commands,
)
app = FastAPI(
    title="Family Beacon API",
    version="0.1.0",
)

@app.post("/device/heartbeat")
async def device_heartbeat_endpoint(
    authorization: str | None = Header(default=None),
):
    return device_heartbeat(authorization)

@app.post("/device/commands/claim")
async def claim_device_command_endpoint(
    authorization: str | None = Header(default=None),
):
    return claim_next_device_command(authorization)



@app.post("/device/commands/recover")
async def recover_stale_device_commands_endpoint(
    authorization: str | None = Header(default=None),
    stale_after_seconds: int = 120,
):
    return recover_stale_device_commands(
        authorization=authorization,
        stale_after_seconds=stale_after_seconds,
    )

@app.get("/families/{family_id}")
async def get_family_endpoint(
    family_id: str,
    auth=Depends(get_current_user),
):
    current_user, access_token = auth

    return get_family(
        access_token=access_token,
        family_id=family_id,
    )

@app.get("/families")
async def list_families_endpoint(
    auth=Depends(get_current_user),
):
    current_user, access_token = auth

    return list_families(
        access_token=access_token,
    )

@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/supabase-check")
async def supabase_check() -> dict[str, bool | str]:
    if supabase is None:
        return {
            "connected": False,
            "error": "Supabase configuration is missing",
        }

    try:
        response = supabase.rpc("health_check").execute()

        return {
            "connected": True,
            "query_ok": response.data is not None,
        }

    except Exception as exc:
        return {
            "connected": False,
            "error": str(exc),
        }


@app.get("/me")
async def me(auth=Depends(get_current_user)):
    current_user, access_token = auth

    profile = get_profile(
        str(current_user.id),
        access_token,
    )

    return {
        "user": {
            "id": str(current_user.id),
            "email": current_user.email,
        },
        "profile": profile,
    }


class CreateFamilyRequest(BaseModel):
    name: str




class RedeemFamilyInviteRequest(BaseModel):
    code: str


@app.post("/families/redeem-invite")
async def redeem_family_invite_endpoint(
    data: RedeemFamilyInviteRequest,
    auth=Depends(get_current_user),
):
    current_user, access_token = auth

    user_client = get_user_client(access_token)

    try:
        return redeem_family_invite(
            user_client,
            data.code,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

@app.post("/families")
async def create_family(
    data: CreateFamilyRequest,
    auth=Depends(get_current_user),
):
    current_user, access_token = auth

    user_client = get_user_client(access_token)

    response = (
        user_client
        .rpc("create_family", {"family_name": data.name})
        .execute()
    )

    return {
        "family_id": response.data,
    }


@app.post("/children")
async def create_child_endpoint(
    family_id: str,
    data: CreateChildRequest,
    auth=Depends(get_current_user),
):
    current_user, access_token = auth

    return create_child(
        access_token=access_token,
        family_id=family_id,
        data=data,
    )


@app.get("/children")
async def list_children_endpoint(
    family_id: str,
    auth=Depends(get_current_user),
):
    current_user, access_token = auth

    return list_children(
        access_token=access_token,
        family_id=family_id,
    )


@app.post("/devices")
async def create_device_endpoint(
    data: CreateDeviceRequest,
    auth=Depends(get_current_user),
):
    current_user, access_token = auth

    return create_device(
        access_token=access_token,
        data=data,
    )


@app.get("/devices")
async def list_devices_endpoint(
    child_id: str | None = None,
    auth=Depends(get_current_user),
):
    current_user, access_token = auth

    return list_devices(
        access_token=access_token,
        child_id=child_id,
    )


@app.get("/devices/{device_id}")
async def get_device_endpoint(
    device_id: str,
    auth=Depends(get_current_user),
):
    current_user, access_token = auth

    return get_device(
        access_token=access_token,
        device_id=device_id,
    )


@app.patch("/devices/{device_id}")
async def update_device_endpoint(
    device_id: str,
    data: UpdateDeviceRequest,
    auth=Depends(get_current_user),
):
    current_user, access_token = auth

    return update_device(
        access_token=access_token,
        device_id=device_id,
        data=data,
    )


@app.post("/devices/{device_id}/heartbeat")
async def heartbeat_device_endpoint(
    device_id: str,
    auth=Depends(get_current_user),
):
    current_user, access_token = auth

    return heartbeat_device(
        access_token=access_token,
        device_id=device_id,
    )


@app.delete("/devices/{device_id}")
async def delete_device_endpoint(
    device_id: str,
    auth=Depends(get_current_user),
):
    current_user, access_token = auth

    return delete_device(
        access_token=access_token,
        device_id=device_id,
    )


@app.post("/time-policies")
async def create_time_policy_endpoint(
    data: CreateTimePolicyRequest,
    auth=Depends(get_current_user),
):
    current_user, access_token = auth

    return create_time_policy(
        access_token=access_token,
        data=data,
    )


@app.get("/time-policies")
async def list_time_policies_endpoint(
    child_id: str,
    auth=Depends(get_current_user),
):
    current_user, access_token = auth

    return list_time_policies(
        access_token=access_token,
        child_id=child_id,
    )


@app.get("/time-policies/{policy_id}")
async def get_time_policy_endpoint(
    policy_id: str,
    auth=Depends(get_current_user),
):
    current_user, access_token = auth

    return get_time_policy(
        access_token=access_token,
        policy_id=policy_id,
    )


@app.patch("/time-policies/{policy_id}")
async def update_time_policy_endpoint(
    policy_id: str,
    data: UpdateTimePolicyRequest,
    auth=Depends(get_current_user),
):
    current_user, access_token = auth

    return update_time_policy(
        access_token=access_token,
        policy_id=policy_id,
        data=data,
    )


@app.delete("/time-policies/{policy_id}")
async def delete_time_policy_endpoint(
    policy_id: str,
    auth=Depends(get_current_user),
):
    current_user, access_token = auth

    return delete_time_policy(
        access_token=access_token,
        policy_id=policy_id,
    )


@app.get("/time-usage")
async def list_time_usage_endpoint(
    child_id: str | None = None,
    usage_date: str | None = None,
    auth=Depends(get_current_user),
):
    from datetime import date

    current_user, access_token = auth

    parsed_date = (
        date.fromisoformat(usage_date)
        if usage_date is not None
        else None
    )

    return list_time_usage(
        access_token=access_token,
        child_id=child_id,
        usage_date=parsed_date,
    )


@app.post("/devices/{device_id}/usage")
async def record_time_usage_endpoint(
    device_id: str,
    data: RecordTimeUsageRequest,
    auth=Depends(get_current_user),
):
    current_user, access_token = auth

    return record_time_usage(
        access_token=access_token,
        device_id=device_id,
        data=data,
    )
@app.post("/commands")
async def create_command_endpoint(
    data: CreateCommandRequest,
    auth=Depends(get_current_user),
):
    current_user, access_token = auth

    return create_command(
        access_token=access_token,
        data=data,
    )


@app.get("/commands")
async def list_commands_endpoint(
    device_id: str | None = None,
    auth=Depends(get_current_user),
):
    current_user, access_token = auth

    return list_commands(
        access_token=access_token,
        device_id=device_id,
    )


@app.get("/commands/{command_id}")
async def get_command_endpoint(
    command_id: str,
    auth=Depends(get_current_user),
):
    current_user, access_token = auth

    return get_command(
        access_token=access_token,
        command_id=command_id,
    )

@app.post("/devices/{device_id}/auth-token")
async def create_device_auth_token_endpoint(
    device_id: str,
    auth=Depends(get_current_user),
):
    current_user, access_token = auth

    return create_device_auth_token(
        access_token=access_token,
        device_id=device_id,
    )

@app.post("/device/auth")
async def device_auth_endpoint(
    data: DeviceAuthRequest,
):
    return authenticate_device(data.token)


class CompleteDeviceCommandRequest(BaseModel):
    status: str
    result: dict | None = None
    error_message: str | None = None


@app.post("/device/commands/{command_id}/complete")
async def complete_device_command_endpoint(
    command_id: str,
    data: CompleteDeviceCommandRequest,
    authorization: str | None = Header(default=None),
):
    return complete_device_command(
        authorization=authorization,
        command_id=command_id,
        status=data.status,
        result=data.result,
        error_message=data.error_message,
    )
