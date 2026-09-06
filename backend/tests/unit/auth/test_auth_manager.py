import os

import pytest

from tests.support.auth.client import AuthTestClient
from tests.support.auth.users import AuthTestUser, get_test_user


def test_parent_test_user_is_loaded_from_environment():
    user = get_test_user("parent")

    expected_email = (
        os.getenv("TEST_PARENT_EMAIL")
        or os.environ["TEST_EMAIL"]
    )
    expected_password = (
        os.getenv("TEST_PARENT_PASSWORD")
        or os.environ["TEST_PASSWORD"]
    )

    assert user.email == expected_email
    assert user.password == expected_password
    assert user.expected_role == "parent"


def test_parent_can_authenticate_and_access_me():
    user = get_test_user("parent")

    client = AuthTestClient(user)
    response = client.get("/me")

    assert response.status_code == 200

    data = response.json()

    assert data["user"]["email"] == user.email
    assert data["profile"]["role"] == user.expected_role

    client.close()


def test_missing_parent_email_fails_clearly(monkeypatch):
    monkeypatch.delenv("TEST_PARENT_EMAIL", raising=False)
    monkeypatch.delenv("TEST_EMAIL", raising=False)

    with pytest.raises(
        RuntimeError,
        match="TEST_PARENT_EMAIL or TEST_EMAIL",
    ):
        get_test_user("parent")


def test_missing_parent_password_fails_clearly(monkeypatch):
    monkeypatch.delenv("TEST_PARENT_PASSWORD", raising=False)
    monkeypatch.delenv("TEST_PASSWORD", raising=False)

    with pytest.raises(
        RuntimeError,
        match="TEST_PARENT_PASSWORD or TEST_PASSWORD",
    ):
        get_test_user("parent")


def test_invalid_credentials_fail_without_exposing_password():
    user = AuthTestUser(
        name="invalid",
        email="invalid.familybeacon.test@example.com",
        password="definitely-invalid-password",
        expected_role="parent",
    )

    with pytest.raises(RuntimeError) as exc_info:
        AuthTestClient(user)

    error_text = str(exc_info.value)

    assert "definitely-invalid-password" not in error_text


def test_parent_client_fixture_provides_authenticated_client(parent_client):
    response = parent_client.get("/me")

    assert response.status_code == 200

    data = response.json()

    assert data["profile"]["role"] == "parent"


def test_parent_supabase_client_fixture_is_authenticated(
    parent_supabase_client,
):
    response = (
        parent_supabase_client
        .table("profiles")
        .select("id, role, is_active")
        .limit(1)
        .execute()
    )

    assert response.data
    assert response.data[0]["role"] == "parent"
    assert response.data[0]["is_active"] is True


def test_parent_access_token_fixture_returns_token(parent_access_token):
    assert isinstance(parent_access_token, str)
    assert parent_access_token
