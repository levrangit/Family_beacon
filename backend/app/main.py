from contextlib import asynccontextmanager
import hmac

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
from app.family_invites import create_family_invite, redeem_family_invite
from app.parent_registration import ParentRegistrationRequest, register_parent
from app.time_usage import (
    RecordTimeUsageRequest,
    record_time_usage,
    list_time_usage,
)
from app.profiles import get_profile, lookup_profile_by_telegram_id
from app.config import TELEGRAM_BOT_SHARED_SECRET
from app.supabase_client import close_http_client, get_user_client, supabase
from app.telegram_child import TelegramChildService
from app.telegram_parent import TelegramParentService

from app.commands import (
    CreateCommandRequest,
    create_command,
    list_commands,
    get_command,
)

from app.device_agent import DeviceHeartbeatRequest, device_heartbeat

from app.device_auth import (
    DeviceAuthRequest,
    authenticate_device,
    create_device_auth_token,
    claim_next_device_command,
    complete_device_command,
    recover_stale_device_commands,
)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield
    close_http_client()


app = FastAPI(
    title="Family Beacon API",
    version="0.1.0",
    lifespan=lifespan,
)


@app.post("/device/heartbeat")
async def device_heartbeat_endpoint(
    data: DeviceHeartbeatRequest,
    authorization: str | None = Header(default=None),
):
    return device_heartbeat(
        data=data,
        authorization=authorization,
    )


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


@app.get("/telegram/lookup/{telegram_id}")
async def telegram_lookup_endpoint(
    telegram_id: int,
    x_telegram_bot_key: str | None = Header(default=None),
):
    if not TELEGRAM_BOT_SHARED_SECRET or not x_telegram_bot_key:
        raise HTTPException(status_code=401, detail="Telegram bot authentication required")

    if not hmac.compare_digest(x_telegram_bot_key, TELEGRAM_BOT_SHARED_SECRET):
        raise HTTPException(status_code=403, detail="Invalid Telegram bot authentication")

    profile = lookup_profile_by_telegram_id(telegram_id)

    if profile is None:
        raise HTTPException(status_code=404, detail="Telegram ID not found")

    return profile


def _telegram_parent_service(x_telegram_bot_key: str | None) -> TelegramParentService:
    if not TELEGRAM_BOT_SHARED_SECRET or not x_telegram_bot_key:
        raise HTTPException(status_code=401, detail="Telegram bot authentication required")

    if not hmac.compare_digest(x_telegram_bot_key, TELEGRAM_BOT_SHARED_SECRET):
        raise HTTPException(status_code=403, detail="Invalid Telegram bot authentication")

    try:
        return TelegramParentService()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


def _telegram_child_service(x_telegram_bot_key: str | None) -> TelegramChildService:
    if not TELEGRAM_BOT_SHARED_SECRET or not x_telegram_bot_key:
        raise HTTPException(status_code=401, detail="Telegram bot authentication required")

    if not hmac.compare_digest(x_telegram_bot_key, TELEGRAM_BOT_SHARED_SECRET):
        raise HTTPException(status_code=403, detail="Invalid Telegram bot authentication")

    try:
        return TelegramChildService()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.get("/telegram/parent/profile/{telegram_id}")
async def telegram_parent_profile_endpoint(
    telegram_id: int,
    x_telegram_bot_key: str | None = Header(default=None),
):
    service = _telegram_parent_service(x_telegram_bot_key)
    try:
        return service.get_profile(telegram_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/telegram/parent/family/{telegram_id}")
async def telegram_parent_family_endpoint(
    telegram_id: int,
    x_telegram_bot_key: str | None = Header(default=None),
):
    service = _telegram_parent_service(x_telegram_bot_key)
    try:
        return service.get_family(telegram_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


class TelegramParentFamilyRenameRequest(BaseModel):
    name: str


@app.patch("/telegram/parent/family/{telegram_id}")
async def telegram_parent_family_rename_endpoint(
    telegram_id: int,
    data: TelegramParentFamilyRenameRequest,
    x_telegram_bot_key: str | None = Header(default=None),
):
    service = _telegram_parent_service(x_telegram_bot_key)
    try:
        return service.rename_family(telegram_id, data.name)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/telegram/parent/children/{telegram_id}")
async def telegram_parent_children_endpoint(
    telegram_id: int,
    x_telegram_bot_key: str | None = Header(default=None),
):
    service = _telegram_parent_service(x_telegram_bot_key)
    try:
        return service.get_children(telegram_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/telegram/parent/children/{telegram_id}/{child_id}/dashboard")
async def telegram_parent_child_dashboard_endpoint(
    telegram_id: int,
    child_id: str,
    x_telegram_bot_key: str | None = Header(default=None),
):
    service = _telegram_parent_service(x_telegram_bot_key)
    try:
        return service.get_child_dashboard(telegram_id, child_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/telegram/parent/invites/{telegram_id}")
async def telegram_parent_invites_endpoint(
    telegram_id: int,
    x_telegram_bot_key: str | None = Header(default=None),
):
    service = _telegram_parent_service(x_telegram_bot_key)
    try:
        return service.list_invites(telegram_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/telegram/parent/invites/{telegram_id}")
async def telegram_parent_create_invite_endpoint(
    telegram_id: int,
    x_telegram_bot_key: str | None = Header(default=None),
):
    service = _telegram_parent_service(x_telegram_bot_key)
    try:
        return service.create_child_invite(telegram_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


class TelegramChildRegistrationRequest(BaseModel):
    telegram_id: int
    invite_code: str
    child_name: str


@app.post("/telegram/child/register")
async def telegram_child_register_endpoint(
    data: TelegramChildRegistrationRequest,
    x_telegram_bot_key: str | None = Header(default=None),
):
    service = _telegram_child_service(x_telegram_bot_key)
    try:
        return service.register_child(
            telegram_id=data.telegram_id,
            invite_code=data.invite_code,
            child_name=data.child_name,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.delete("/telegram/parent/account/{telegram_id}")
async def telegram_parent_delete_account_endpoint(
    telegram_id: int,
    x_telegram_bot_key: str | None = Header(default=None),
):
    service = _telegram_parent_service(x_telegram_bot_key)
    try:
        return service.delete_parent_account(telegram_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


class ParentRegistrationRequest(BaseModel):
    telegram_id: int
    login: str
    password: str


class CreateFamilyRequest(BaseModel):
    name: str


class RedeemFamilyInviteRequest(BaseModel):
    code: str


@app.post("/auth/register-parent")
async def register_parent_endpoint(
    data: ParentRegistrationRequest,
    x_telegram_bot_key: str | None = Header(default=None),
):
    if not TELEGRAM_BOT_SHARED_SECRET or not x_telegram_bot_key:
        raise HTTPException(status_code=401, detail="Telegram bot authentication required")

    if not hmac.compare_digest(x_telegram_bot_key, TELEGRAM_BOT_SHARED_SECRET):
        raise HTTPException(status_code=403, detail="Invalid Telegram bot authentication")

    if supabase is None:
        raise HTTPException(
            status_code=503,
            detail="Supabase configuration is missing",
        )

    try:
        return register_parent(supabase, data)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@app.post("/families/{family_id}/invite")
async def create_family_invite_endpoint(
    family_id: str,
    auth=Depends(get_current_user),
):
    current_user, access_token = auth

    user_client = get_user_client(access_token)

    try:
        return create_family_invite(
            user_client,
            family_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


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


@app.post("/time-usage")
async def record_time_usage_endpoint(
    data: RecordTimeUsageRequest,
    auth=Depends(get_current_user),
):
    current_user, access_token = auth

    return record_time_usage(
        access_token=access_token,
        data=data,
    )


@app.get("/time-usage")
async def list_time_usage_endpoint(
    child_id: str,
    auth=Depends(get_current_user),
):
    current_user, access_token = auth

    return list_time_usage(
        access_token=access_token,
        child_id=child_id,
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


@app.post("/device/auth")
async def device_auth_endpoint(data: DeviceAuthRequest):
    return authenticate_device(data)


@app.post("/device/auth/token")
async def device_auth_token_endpoint(data: DeviceAuthRequest):
    return create_device_auth_token(data)


@app.post("/device/commands/complete")
async def complete_device_command_endpoint(
    authorization: str | None = Header(default=None),
):
    return complete_device_command(authorization)


@app.get("/telegram/child/{telegram_id}/dashboard")
async def telegram_child_dashboard_endpoint(
    telegram_id: int,
    x_telegram_bot_key: str | None = Header(default=None),
):
    service = _telegram_child_service(x_telegram_bot_key)
    try:
        return service.get_dashboard(telegram_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


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
