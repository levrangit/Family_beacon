from unittest.mock import Mock

from app.parent_registration import ParentRegistrationRequest
from app.parent_registration import register_parent


def test_register_parent_passes_telegram_id_to_supabase_auth():
    supabase_client = Mock()

    supabase_client.auth.sign_up.return_value = Mock(
        user=Mock(id="user-123"),
        session=Mock(access_token="access-token-123"),
    )

    request = ParentRegistrationRequest(
        telegram_id=123456789,
        login="parent@example.com",
        password="secret123",
    )

    result = register_parent(
        supabase_client=supabase_client,
        request=request,
    )

    supabase_client.auth.sign_up.assert_called_once_with(
        {
            "email": "parent@example.com",
            "password": "secret123",
            "options": {
                "data": {
                    "telegram_id": 123456789,
                }
            },
        }
    )

    assert result["user_id"] == "user-123"
    assert result["access_token"] == "access-token-123"
