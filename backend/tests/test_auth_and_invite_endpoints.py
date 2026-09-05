from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from app.auth import get_current_user
from app.main import app


TEST_TELEGRAM_BOT_KEY = "test-telegram-bot-key"
TELEGRAM_BOT_HEADERS = {
    "X-Telegram-Bot-Key": TEST_TELEGRAM_BOT_KEY,
}


def test_register_parent_endpoint_uses_register_parent_service(monkeypatch):
    import app.main as main

    monkeypatch.setattr(main, "TELEGRAM_BOT_SHARED_SECRET", TEST_TELEGRAM_BOT_KEY)

    expected = {
        "user_id": "user-123",
        "access_token": "access-token-123",
    }
    calls = {}
    mock_supabase = MagicMock()

    def fake_register_parent(client, request):
        calls["client"] = client
        calls["request"] = request
        return expected

    monkeypatch.setattr(main, "register_parent", fake_register_parent)
    original_supabase = main.supabase
    main.supabase = mock_supabase

    try:
        response = TestClient(app).post(
            "/auth/register-parent",
            json={
                "telegram_id": 123456789,
                "login": "parent2@example.com",
                "password": "secret123",
            },
            headers=TELEGRAM_BOT_HEADERS,
        )
    finally:
        main.supabase = original_supabase

    assert response.status_code == 200
    assert response.json() == expected
    assert calls["client"] is mock_supabase
    assert calls["request"].telegram_id == 123456789
    assert calls["request"].login == "parent2@example.com"
    assert calls["request"].password == "secret123"


def test_create_family_invite_endpoint_uses_create_family_invite_service(monkeypatch):
    import app.main as main

    access_token = "parent-access-token"
    app.dependency_overrides[get_current_user] = lambda: (
        MagicMock(id="parent-user-id"),
        access_token,
    )
    mock_user_client = MagicMock()
    calls = {}

    def fake_create_family_invite(client, family_id):
        calls["client"] = client
        calls["family_id"] = family_id
        return {
            "invite_id": "invite-123",
            "family_id": family_id,
            "code": "7K4M-92QX",
            "expires_at": "2026-09-03T12:00:00+00:00",
        }

    monkeypatch.setattr(main, "create_family_invite", fake_create_family_invite)
    original_get_user_client = main.get_user_client
    main.get_user_client = lambda token: mock_user_client

    try:
        response = TestClient(app).post("/families/family-123/invite")
    finally:
        main.get_user_client = original_get_user_client
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "invite_id": "invite-123",
        "family_id": "family-123",
        "code": "7K4M-92QX",
        "expires_at": "2026-09-03T12:00:00+00:00",
    }
    assert calls["client"] is mock_user_client
    assert calls["family_id"] == "family-123"
