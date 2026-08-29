
from fastapi import Depends, FastAPI
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
from app.families import get_family, list_families
from app.profiles import get_profile
from app.supabase_client import get_user_client, supabase

app = FastAPI(
    title="Family Beacon API",
    version="0.1.0",
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
