import uuid

import httpx
import pytest
from supabase import ClientOptions, create_client

from app.config import SUPABASE_SERVICE_ROLE_KEY
from tests_backend.support.auth.client import AuthTestClient, SUPABASE_KEY, SUPABASE_URL
from tests_backend.support.auth.temporary_users import (
    TemporaryUserManager,
    require_temporary_user_configuration,
)


SUPABASE_HTTP_TIMEOUT = 120.0


@pytest.fixture(scope="session")
def supabase_service_client():
    if not SUPABASE_SERVICE_ROLE_KEY:
        pytest.fail(
            "SUPABASE_SERVICE_ROLE_KEY is required for tests that create "
            "temporary remote users or perform cleanup"
        )

    http_client = httpx.Client(timeout=httpx.Timeout(SUPABASE_HTTP_TIMEOUT))
    supabase = create_client(
        SUPABASE_URL,
        SUPABASE_SERVICE_ROLE_KEY,
        options=ClientOptions(httpx_client=http_client),
    )

    try:
        yield supabase
    finally:
        http_client.close()


@pytest.fixture
def temporary_user_manager(supabase_service_client):
    require_temporary_user_configuration()
    manager = TemporaryUserManager(supabase_service_client)
    try:
        yield manager
    finally:
        manager.cleanup()


@pytest.fixture
def temporary_parent_user(temporary_user_manager):
    return temporary_user_manager.create("parent")


@pytest.fixture
def parent_supabase_client(temporary_user_manager, temporary_parent_user):
    return temporary_user_manager.client(temporary_parent_user)


@pytest.fixture
def parent_family_id(parent_supabase_client, supabase_service_client):
    response = parent_supabase_client.rpc(
        "create_family",
        {"family_name": f"pytest-family-{uuid.uuid4().hex}"},
    ).execute()

    if response.data is None:
        pytest.fail("Temporary test family ID was not returned")

    family_id = str(response.data)

    try:
        yield family_id
    finally:
        supabase_service_client.table("families").delete().eq(
            "id", family_id
        ).execute()


@pytest.fixture
def invite_redeemer_supabase_client(temporary_user_manager):
    user = temporary_user_manager.create("invite-redeemer")
    return temporary_user_manager.client(user)


@pytest.fixture
def parent_client(temporary_parent_user):
    client = AuthTestClient(temporary_parent_user)

    try:
        response = client.get("/me")

        if response.status_code != 200:
            raise RuntimeError(
                f"Test parent authentication check failed: "
                f"HTTP {response.status_code}"
            )

        data = response.json()

        if data.get("profile", {}).get("role") != "parent":
            raise RuntimeError(
                "Test parent authentication check failed: "
                "expected profile role 'parent'"
            )

        yield client
    finally:
        client.close()


@pytest.fixture
def parent_access_token(parent_client):
    return parent_client.access_token
