from telegram_bot.backend_client import BackendClient


def test_register_parent_sends_registration_data_to_backend():
    client = BackendClient("http://127.0.0.1:8000")

    result = client.register_parent(
        telegram_id=123456789,
        login="parent@example.com",
        password="SecretPassword123",
    )

    assert result["telegram_id"] == 123456789
    assert result["login"] == "parent@example.com"
