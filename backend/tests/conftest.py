import os
import uuid

import httpx
import pytest
from supabase import ClientOptions, create_client

from tests.auth.client import AuthTestClient, SUPABASE_KEY, SUPABASE_URL
from app.config import SUPABASE_SERVICE_ROLE_KEY
from tests.auth.users import get_test_user


SUPABASE_HTTP_TIMEOUT = 120.0


@pytest.fixture(scope="session")
def parent_supabase_client():
    user = get_test_user("parent")
    http_client = httpx.Client(
        timeout=httpx.Timeout(SUPABASE_HTTP_TIMEOUT),
    )
    supabase = create_client(
        SUPABASE_URL,
        SUPABASE_KEY,
        options=ClientOptions(httpx_client=http_client),
    )

    response = supabase.auth.sign_in_with_password(
        {
            "email": user.email,
            "password": user.password,
        }
    )

    if not response.session:
        http_client.close()
        raise RuntimeError(
            "Test parent Supabase authentication did not return a session"
        )

    access_token = response.session.access_token

    if not access_token:
        http_client.close()
        raise RuntimeError(
            "Test parent Supabase authentication did not return an access token"
        )

    supabase.postgrest.auth(access_token)

    try:
        yield supabase
    finally:
        http_client.close()


@pytest.fixture(scope="session")
def supabase_service_client():
    if not SUPABASE_SERVICE_ROLE_KEY:
        pytest.skip("SUPABASE_SERVICE_ROLE_KEY is required for tests that create temporary remote users")

    http_client = httpx.Client(
        timeout=httpx.Timeout(SUPABASE_HTTP_TIMEOUT),
    )
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
def invite_redeemer_supabase_client(supabase_service_client):
    email = f"pytest-invite-redeemer-{uuid.uuid4().hex}@example.com"
    password = f"Test-{uuid.uuid4().hex}-Aa1!"
    http_client = httpx.Client(
        timeout=httpx.Timeout(SUPABASE_HTTP_TIMEOUT),
    )
    supabase = create_client(
        SUPABASE_URL,
        SUPABASE_KEY,
        options=ClientOptions(httpx_client=http_client),
    )

    user_id = None

    try:
        response = supabase.auth.sign_up(
            {
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "telegram_id": int(uuid.uuid4().int % 2_000_000_000),
                    }
                },
            }
        )

        if response.user is None:
            raise RuntimeError("Test invite redeemer registration did not return a user")

        user_id = response.user.id

        if not response.session:
            raise RuntimeError(
                "Test invite redeemer authentication did not return a session"
            )

        access_token = response.session.access_token

        if not access_token:
            raise RuntimeError(
                "Test invite redeemer authentication did not return an access token"
            )

        supabase.postgrest.auth(access_token)
        supabase.test_access_token = access_token
        yield supabase
    finally:
        if user_id is not None:
            supabase_service_client.auth.admin.delete_user(user_id)
        http_client.close()


@pytest.fixture(scope="session")
def parent_client():
    user = get_test_user("parent")
    client = AuthTestClient(user)

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


@pytest.fixture(scope="session")
def parent_access_token(parent_client):
    return parent_client.access_token
