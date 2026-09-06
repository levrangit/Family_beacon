import hashlib
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.device_auth import (
    TOKEN_PREFIX,
    authenticate_device,
    authenticate_device_token,
    claim_next_device_command,
    complete_device_command,
    create_device_auth_token,
    get_device_token_hash,
    recover_stale_device_commands,
)


def test_get_device_token_hash_requires_authorization():
    with pytest.raises(HTTPException) as exc:
        get_device_token_hash(None)
    assert exc.value.status_code == 401
    assert exc.value.detail == "Device authorization is required"


def test_get_device_token_hash_requires_bearer():
    with pytest.raises(HTTPException) as exc:
        get_device_token_hash("Basic token")
    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid device authorization"


def test_get_device_token_hash_requires_prefix():
    with pytest.raises(HTTPException) as exc:
        get_device_token_hash("Bearer wrong-token")
    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid device token"


def test_get_device_token_hash_hashes_valid_token():
    token = TOKEN_PREFIX + "secret"
    assert get_device_token_hash(f"Bearer {token}") == hashlib.sha256(token.encode()).hexdigest()


def test_create_device_auth_token_requires_user_token(monkeypatch):
    with pytest.raises(HTTPException) as exc:
        create_device_auth_token("", "device-1")
    assert exc.value.status_code == 401


def test_create_device_auth_token_requires_device_id(monkeypatch):
    with pytest.raises(HTTPException) as exc:
        create_device_auth_token("token", "")
    assert exc.value.status_code == 400


def test_create_device_auth_token_returns_token(monkeypatch):
    client = MagicMock()
    client.rpc.return_value.execute.return_value.data = [{"ok": True}]
    monkeypatch.setattr("app.device_auth.get_user_client", lambda token: client)

    result = create_device_auth_token("user-token", "device-1")

    assert result["device_id"] == "device-1"
    assert result["token"].startswith(TOKEN_PREFIX)
    assert len(result["token"]) > len(TOKEN_PREFIX)


def test_create_device_auth_token_maps_permission_error(monkeypatch):
    client = MagicMock()
    client.rpc.return_value.execute.side_effect = RuntimeError("Permission denied")
    monkeypatch.setattr("app.device_auth.get_user_client", lambda token: client)

    with pytest.raises(HTTPException) as exc:
        create_device_auth_token("user-token", "device-1")
    assert exc.value.status_code == 403


def test_create_device_auth_token_maps_missing_device(monkeypatch):
    client = MagicMock()
    client.rpc.return_value.execute.side_effect = RuntimeError("Device not found")
    monkeypatch.setattr("app.device_auth.get_user_client", lambda token: client)

    with pytest.raises(HTTPException) as exc:
        create_device_auth_token("user-token", "device-1")
    assert exc.value.status_code == 404


def test_authenticate_device_requires_token(monkeypatch):
    with pytest.raises(HTTPException) as exc:
        authenticate_device("")
    assert exc.value.status_code == 401
    assert exc.value.detail == "Device token is required"


def test_authenticate_device_rejects_wrong_prefix(monkeypatch):
    with pytest.raises(HTTPException) as exc:
        authenticate_device("bad-token")
    assert exc.value.status_code == 401


def test_authenticate_device_returns_device_id(monkeypatch):
    supabase = MagicMock()
    supabase.rpc.return_value.execute.return_value.data = "device-1"
    monkeypatch.setattr("app.device_auth.supabase", supabase)

    token = TOKEN_PREFIX + "secret"
    assert authenticate_device(token) == {"device_id": "device-1"}


def test_authenticate_device_token_returns_device_id(monkeypatch):
    supabase = MagicMock()
    supabase.rpc.return_value.execute.return_value.data = "device-1"
    monkeypatch.setattr("app.device_auth.supabase", supabase)

    result = authenticate_device_token(f"Bearer {TOKEN_PREFIX}secret")
    assert result == "device-1"


def test_claim_next_device_command_returns_none_when_queue_empty(monkeypatch):
    supabase = MagicMock()
    supabase.rpc.return_value.execute.return_value.data = None
    monkeypatch.setattr("app.device_auth.supabase", supabase)

    assert claim_next_device_command(f"Bearer {TOKEN_PREFIX}secret") is None


def test_complete_device_command_maps_invalid_status(monkeypatch):
    supabase = MagicMock()
    supabase.rpc.return_value.execute.side_effect = RuntimeError("Invalid command status")
    monkeypatch.setattr("app.device_auth.supabase", supabase)

    with pytest.raises(HTTPException) as exc:
        complete_device_command(
            f"Bearer {TOKEN_PREFIX}secret",
            "command-1",
            "bad",
        )
    assert exc.value.status_code == 400


def test_complete_device_command_returns_rpc_result(monkeypatch):
    supabase = MagicMock()
    supabase.rpc.return_value.execute.return_value.data = {"status": "completed"}
    monkeypatch.setattr("app.device_auth.supabase", supabase)

    result = complete_device_command(
        f"Bearer {TOKEN_PREFIX}secret",
        "command-1",
        "completed",
        {"ok": True},
        None,
    )

    assert result == {"status": "completed"}


def test_recover_stale_device_commands_returns_empty_list(monkeypatch):
    supabase = MagicMock()
    supabase.rpc.return_value.execute.return_value.data = None
    monkeypatch.setattr("app.device_auth.supabase", supabase)

    assert recover_stale_device_commands(f"Bearer {TOKEN_PREFIX}secret") == []
