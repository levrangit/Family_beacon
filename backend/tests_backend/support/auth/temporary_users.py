import uuid
from dataclasses import dataclass

import httpx
import pytest
from supabase import ClientOptions, create_client

from app.config import SUPABASE_SERVICE_ROLE_KEY

from .client import SUPABASE_HTTP_TIMEOUT, SUPABASE_KEY, SUPABASE_URL


@dataclass(frozen=True)
class AuthTestUser:
    name: str
    email: str
    password: str
    expected_role: str
    user_id: str


class TemporaryUserManager:
    """Create and clean up isolated Supabase Auth users for real-service tests."""

    def __init__(self, service_client):
        self.service_client = service_client
        self._users: list[AuthTestUser] = []
        self._clients: list[httpx.Client] = []

    def create(self, name: str, expected_role: str = "parent") -> AuthTestUser:
        email = f"pytest-{name}-{uuid.uuid4().hex}@example.com"
        password = f"Test-{uuid.uuid4().hex}-Aa1!"
        telegram_id = int(uuid.uuid4().int % 2_000_000_000)

        response = self.service_client.auth.admin.create_user(
            {
                "email": email,
                "password": password,
                "email_confirm": True,
                "user_metadata": {"telegram_id": telegram_id},
            }
        )

        if response.user is None:
            pytest.fail(f"Temporary {name} Auth user was not created")

        user = AuthTestUser(
            name=name,
            email=email,
            password=password,
            expected_role=expected_role,
            user_id=response.user.id,
        )
        self._users.append(user)
        return user

    def client(self, user: AuthTestUser):
        http_client = httpx.Client(timeout=httpx.Timeout(SUPABASE_HTTP_TIMEOUT))
        self._clients.append(http_client)
        supabase = create_client(
            SUPABASE_URL,
            SUPABASE_KEY,
            options=ClientOptions(httpx_client=http_client),
        )

        response = supabase.auth.sign_in_with_password(
            {"email": user.email, "password": user.password}
        )

        if not response.session or not response.session.access_token:
            http_client.close()
            self._clients.remove(http_client)
            raise RuntimeError(
                f"Temporary {user.name} Auth user authentication did not return an access token"
            )

        supabase.postgrest.auth(response.session.access_token)
        supabase.test_access_token = response.session.access_token
        supabase.test_user_id = user.user_id
        return supabase

    def cleanup(self):
        errors = []

        for user in reversed(self._users):
            try:
                self.service_client.auth.admin.delete_user(user.user_id)
            except Exception:
                errors.append(f"temporary Auth user {user.user_id}")

        for http_client in reversed(self._clients):
            try:
                http_client.close()
            except Exception:
                errors.append("temporary Auth HTTP client")

        if errors:
            raise RuntimeError("Cleanup failed: " + ", ".join(errors))


def cleanup_resources(*resources):
    """Run all cleanup callbacks in order and report every failure."""
    errors = []

    for name, callback in resources:
        try:
            callback()
        except Exception:
            errors.append(name)

    if errors:
        raise RuntimeError("Cleanup failed: " + ", ".join(errors))


def require_temporary_user_configuration():
    if not SUPABASE_SERVICE_ROLE_KEY:
        pytest.fail(
            "SUPABASE_SERVICE_ROLE_KEY is required for tests that create temporary users"
        )
