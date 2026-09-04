import asyncio

from telegram_bot.backend_client import BackendClient


class FakeResponse:
    status_code = 200

    def raise_for_status(self):
        return None

    def json(self):
        return {"user_id": "user-1", "access_token": "token"}


class FakeAsyncClient:
    def __init__(self, calls):
        self.calls = calls

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return None

    async def post(self, url, json, headers):
        self.calls.append((url, json, headers))
        return FakeResponse()


def test_register_parent_sends_registration_data_to_backend(monkeypatch):
    calls = []

    def fake_async_client(**_kwargs):
        return FakeAsyncClient(calls)

    monkeypatch.setattr(
        "telegram_bot.backend_client.httpx.AsyncClient",
        fake_async_client,
    )

    client = BackendClient(
        "http://127.0.0.1:8000",
        "test-shared-secret",
    )

    async def run_test():
        result = await client.register_parent(
            telegram_id=123456789,
            login="parent@example.com",
            password="test-password",
        )

        assert result["user_id"] == "user-1"
        assert calls == [
            (
                "http://127.0.0.1:8000/auth/register-parent",
                {
                    "telegram_id": 123456789,
                    "login": "parent@example.com",
                    "password": "test-password",
                },
                {"X-Telegram-Bot-Key": "test-shared-secret"},
            )
        ]

    asyncio.run(run_test())
