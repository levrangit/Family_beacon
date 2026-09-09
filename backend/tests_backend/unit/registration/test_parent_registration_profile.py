from unittest.mock import Mock

from app.parent_registration import ParentRegistrationRequest
from app.parent_registration import register_parent


def test_parent_registration_sends_telegram_id_in_user_metadata():
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

    register_parent(
        supabase_client=supabase_client,
        request=request,
    )

    call_arguments = supabase_client.auth.sign_up.call_args.args[0]

    assert call_arguments["options"]["data"]["telegram_id"] == 123456789
