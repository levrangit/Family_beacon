from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.main import app


TEST_TELEGRAM_BOT_KEY = "test-telegram-bot-key"
TELEGRAM_BOT_HEADERS = {
    "X-Telegram-Bot-Key": TEST_TELEGRAM_BOT_KEY,
}


def test_parent_registration_endpoint_returns_user_and_token(monkeypatch):
    import app.main as main

    monkeypatch.setattr(main, "TELEGRAM_BOT_SHARED_SECRET", TEST_TELEGRAM_BOT_KEY)

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.user = MagicMock(id="user-123")
    mock_response.session = MagicMock(access_token="access-token-123")
    mock_client.auth.sign_up.return_value = mock_response

    original_supabase = main.supabase
    main.supabase = mock_client

    try:
        client = TestClient(app)
        response = client.post(
            "/auth/register-parent",
            json={
                "telegram_id": 123456789,
                "login": "parent2@example.com",
                "password": "secret123",
            },
            headers=TELEGRAM_BOT_HEADERS,
        )

        assert response.status_code == 200
        assert response.json() == {
            "user_id": "user-123",
            "access_token": "access-token-123",
        }
        mock_client.auth.sign_up.assert_called_once_with(
            {
                "email": "parent2@example.com",
                "password": "secret123",
                "options": {"data": {"telegram_id": 123456789}},
            }
        )
    finally:
        main.supabase = original_supabase
        app.dependency_overrides.clear()


def test_parent_registration_endpoint_requires_supabase_configuration(monkeypatch):
    import app.main as main

    monkeypatch.setattr(main, "TELEGRAM_BOT_SHARED_SECRET", TEST_TELEGRAM_BOT_KEY)

    original_supabase = main.supabase
    main.supabase = None

    try:
        client = TestClient(app)
        response = client.post(
            "/auth/register-parent",
            json={
                "telegram_id": 123456789,
                "login": "parent2@example.com",
                "password": "secret123",
            },
            headers=TELEGRAM_BOT_HEADERS,
        )

        assert response.status_code == 503
        assert response.json()["detail"] == "Supabase configuration is missing"
    finally:
        main.supabase = original_supabase
        app.dependency_overrides.clear()


def test_parent_registration_endpoint_delegates_to_register_parent_service(monkeypatch):
    import app.main as main

    monkeypatch.setattr(main, "TELEGRAM_BOT_SHARED_SECRET", TEST_TELEGRAM_BOT_KEY)

    original_supabase = main.supabase
    main.supabase = MagicMock()
    expected = {
        "user_id": "user-123",
        "access_token": "access-token-123",
    }

    try:
        with patch.object(main, "register_parent", return_value=expected) as mock_register:
            response = TestClient(app).post(
                "/auth/register-parent",
                json={
                    "telegram_id": 123456789,
                    "login": "parent2@example.com",
                    "password": "secret123",
                },
                headers=TELEGRAM_BOT_HEADERS,
            )

        assert response.status_code == 200
        assert response.json() == expected
        request = mock_register.call_args.args[1]
        assert request.telegram_id == 123456789
        assert str(request.login) == "parent2@example.com"
        assert request.password == "secret123"
    finally:
        main.supabase = original_supabase
        app.dependency_overrides.clear()
