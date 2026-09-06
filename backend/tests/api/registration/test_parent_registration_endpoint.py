from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.auth import get_current_user
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


def test_create_family_invite_endpoint_returns_invite_code():
    access_token = "parent-access-token"
    app.dependency_overrides[get_current_user] = lambda: (
        MagicMock(id="parent-user-id"),
        access_token,
    )

    mock_user_client = MagicMock()
    rpc_response = MagicMock()
    rpc_response.data = [
        {
            "id": "invite-123",
            "family_id": "family-123",
            "expires_at": "2026-09-03T12:00:00+00:00",
        }
    ]
    mock_user_client.rpc.return_value.execute.return_value = rpc_response

    from app import main
    from app import family_invites

    original_get_user_client = main.get_user_client
    original_generate_invite_code = family_invites.generate_invite_code
    original_hash_invite_code = family_invites.hash_invite_code
    main.get_user_client = lambda token: mock_user_client
    family_invites.generate_invite_code = lambda: "7K4M-92QX"
    family_invites.hash_invite_code = lambda code: "hashed-invite-code"

    try:
        client = TestClient(app)
        response = client.post("/families/family-123/invite")

        assert response.status_code == 200
        assert response.json() == {
            "invite_id": "invite-123",
            "family_id": "family-123",
            "code": "7K4M-92QX",
            "expires_at": "2026-09-03T12:00:00+00:00",
        }
        mock_user_client.rpc.assert_called_once()
        assert mock_user_client.rpc.call_args.args[0] == "create_family_invite"
        assert mock_user_client.rpc.call_args.args[1]["p_family_id"] == "family-123"
        assert mock_user_client.rpc.call_args.args[1]["p_code_hash"] == "hashed-invite-code"
    finally:
        main.get_user_client = original_get_user_client
        family_invites.generate_invite_code = original_generate_invite_code
        family_invites.hash_invite_code = original_hash_invite_code
        app.dependency_overrides.clear()


def test_create_family_invite_endpoint_delegates_to_create_family_invite_service():
    from app import main

    access_token = "parent-access-token"
    app.dependency_overrides[get_current_user] = lambda: (
        MagicMock(id="parent-user-id"),
        access_token,
    )
    mock_user_client = MagicMock()
    original_get_user_client = main.get_user_client
    main.get_user_client = lambda token: mock_user_client
    expected = {
        "invite_id": "invite-123",
        "family_id": "family-123",
        "code": "7K4M-92QX",
        "expires_at": "2026-09-03T12:00:00+00:00",
    }

    try:
        with patch.object(
            main,
            "create_family_invite",
            return_value=expected,
        ) as mock_create_invite:
            response = TestClient(app).post("/families/family-123/invite")

        assert response.status_code == 200
        assert response.json() == expected
        mock_create_invite.assert_called_once_with(
            mock_user_client,
            "family-123",
        )
    finally:
        main.get_user_client = original_get_user_client
        app.dependency_overrides.clear()
