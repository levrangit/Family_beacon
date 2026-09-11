import pytest

from tests_backend.support.auth.client import AuthTestClient
from tests_backend.support.auth.users import AuthTestUser


@pytest.mark.integration
def test_invalid_credentials_fail_without_exposing_password():
    user = AuthTestUser(
        name="invalid",
        email="invalid.familybeacon.test@example.com",
        password="definitely-invalid-password",
        expected_role="parent",
        user_id="invalid-user-id",
    )

    with pytest.raises(RuntimeError) as exc_info:
        AuthTestClient(user)

    error_text = str(exc_info.value)

    assert "definitely-invalid-password" not in error_text


@pytest.mark.integration
def test_parent_can_authenticate_and_access_me(parent_client):
    response = parent_client.get("/me")

    assert response.status_code == 200

    data = response.json()

    assert data["user"]["email"] == parent_client.user.email
    assert data["profile"]["role"] == parent_client.user.expected_role


@pytest.mark.integration
def test_parent_client_fixture_provides_authenticated_client(parent_client):
    response = parent_client.get("/me")

    assert response.status_code == 200

    data = response.json()

    assert data["profile"]["role"] == "parent"


@pytest.mark.integration
def test_parent_supabase_client_fixture_is_authenticated(parent_supabase_client):
    response = (
        parent_supabase_client
        .table("profiles")
        .select("id, role, is_active")
        .eq("id", parent_supabase_client.test_user_id)
        .single()
        .execute()
    )

    assert response.data
    assert response.data["id"] == parent_supabase_client.test_user_id
    assert response.data["role"] == "parent"
    assert response.data["is_active"] is True


@pytest.mark.integration
def test_parent_access_token_fixture_returns_token(parent_access_token):
    assert isinstance(parent_access_token, str)
    assert parent_access_token
