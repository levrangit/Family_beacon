import pytest
from supabase import create_client

from tests.auth.client import AuthTestClient, SUPABASE_KEY, SUPABASE_URL
from tests.auth.users import get_test_user


@pytest.fixture(scope="session")
def parent_supabase_client():
    user = get_test_user("parent")

    supabase = create_client(
        SUPABASE_URL,
        SUPABASE_KEY,
    )

    response = supabase.auth.sign_in_with_password(
        {
            "email": user.email,
            "password": user.password,
        }
    )

    if not response.session:
        raise RuntimeError(
            "Test parent Supabase authentication did not return a session"
        )

    access_token = response.session.access_token

    if not access_token:
        raise RuntimeError(
            "Test parent Supabase authentication did not return an access token"
        )

    supabase.postgrest.auth(access_token)

    yield supabase


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
