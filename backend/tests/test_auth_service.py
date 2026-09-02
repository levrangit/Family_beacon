import asyncio
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.auth import get_current_user


def test_get_current_user_requires_supabase(monkeypatch):
    monkeypatch.setattr("app.auth.supabase", None)

    with pytest.raises(HTTPException) as exc:
        asyncio.run(get_current_user("Bearer token"))

    assert exc.value.status_code == 500
    assert exc.value.detail == "Supabase configuration is missing"


def test_get_current_user_requires_authorization(monkeypatch):
    monkeypatch.setattr("app.auth.supabase", MagicMock())

    with pytest.raises(HTTPException) as exc:
        asyncio.run(get_current_user(None))

    assert exc.value.status_code == 401
    assert exc.value.detail == "Authorization header is required"


@pytest.mark.parametrize("authorization", ["Basic token", "Token token", "bear token"])
def test_get_current_user_requires_bearer_scheme(monkeypatch, authorization):
    monkeypatch.setattr("app.auth.supabase", MagicMock())

    with pytest.raises(HTTPException) as exc:
        asyncio.run(get_current_user(authorization))

    assert exc.value.status_code == 401
    assert exc.value.detail == "Authorization header must use Bearer token"


def test_get_current_user_rejects_empty_bearer(monkeypatch):
    monkeypatch.setattr("app.auth.supabase", MagicMock())

    with pytest.raises(HTTPException) as exc:
        asyncio.run(get_current_user("Bearer   "))

    assert exc.value.status_code == 401
    assert exc.value.detail == "Bearer token is empty"


def test_get_current_user_returns_user_and_token(monkeypatch):
    user = SimpleNamespace(id="user-1", email="parent@example.com")
    supabase = MagicMock()
    supabase.auth.get_user.return_value = SimpleNamespace(user=user)
    monkeypatch.setattr("app.auth.supabase", supabase)

    result = asyncio.run(get_current_user("Bearer abc123"))

    assert result == (user, "abc123")
    supabase.auth.get_user.assert_called_once_with("abc123")


def test_get_current_user_rejects_missing_user(monkeypatch):
    supabase = MagicMock()
    supabase.auth.get_user.return_value = SimpleNamespace(user=None)
    monkeypatch.setattr("app.auth.supabase", supabase)

    with pytest.raises(HTTPException) as exc:
        asyncio.run(get_current_user("Bearer abc123"))

    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid authentication token"


def test_get_current_user_maps_supabase_error_to_401(monkeypatch):
    supabase = MagicMock()
    supabase.auth.get_user.side_effect = RuntimeError("upstream failure")
    monkeypatch.setattr("app.auth.supabase", supabase)

    with pytest.raises(HTTPException) as exc:
        asyncio.run(get_current_user("Bearer abc123"))

    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid authentication token"
