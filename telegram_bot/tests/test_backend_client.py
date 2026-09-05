import asyncio

from telegram_bot.backend_client import BackendClient


class FakeResponse:
    status_code = 200

    def __init__(self, payload=None):
        self.payload = payload or {"user_id": "user-1", "access_token": "token"}

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


class FakeAsyncClient:
    def __init__(self, calls, response_payload=None):
        self.calls = calls
        self.response_payload = response_payload

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return None

    async def post(self, url, json=None, headers=None):
        self.calls.append((url, json, headers))
        return FakeResponse(self.response_payload)


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


def test_register_child_sends_registration_data_to_backend(monkeypatch):
    calls = []

    def fake_async_client(**_kwargs):
        return FakeAsyncClient(
            calls,
            response_payload={
                "child_id": "child-1",
                "family_id": "family-1",
                "invite_id": "invite-1",
            },
        )

    monkeypatch.setattr(
        "telegram_bot.backend_client.httpx.AsyncClient",
        fake_async_client,
    )

    client = BackendClient(
        "http://127.0.0.1:8000",
        "test-shared-secret",
    )

    async def run_test():
        result = await client.register_child(
            telegram_id=123456789,
            invite_code="ABCD-2345",
            child_name="Alice",
        )

        assert result == {
            "child_id": "child-1",
            "family_id": "family-1",
            "invite_id": "invite-1",
        }
        assert calls == [
            (
                "http://127.0.0.1:8000/telegram/child/register",
                {
                    "telegram_id": 123456789,
                    "invite_code": "ABCD-2345",
                    "child_name": "Alice",
                },
                {"X-Telegram-Bot-Key": "test-shared-secret"},
            )
        ]

    asyncio.run(run_test())


def test_create_parent_invite_sends_telegram_id_and_shared_secret(monkeypatch):
    calls = []

    def fake_async_client(**_kwargs):
        return FakeAsyncClient(
            calls,
            response_payload={
                "code": "ABCD1234",
                "expires_at": "2026-09-06T01:30:00+00:00",
            },
        )

    monkeypatch.setattr(
        "telegram_bot.backend_client.httpx.AsyncClient",
        fake_async_client,
    )

    client = BackendClient(
        "http://127.0.0.1:8000",
        "test-shared-secret",
    )

    async def run_test():
        result = await client.create_parent_invite(123456)

        assert result == {
            "code": "ABCD1234",
            "expires_at": "2026-09-06T01:30:00+00:00",
        }
        assert calls == [
            (
                "http://127.0.0.1:8000/telegram/parent/invites/123456",
                None,
                {"X-Telegram-Bot-Key": "test-shared-secret"},
            )
        ]

    asyncio.run(run_test())
