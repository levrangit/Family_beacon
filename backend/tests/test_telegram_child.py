from app.invite_code import hash_invite_code
from app.telegram_child import TelegramChildService


class Response:
    def __init__(self, data):
        self.data = data


class RpcQuery:
    def __init__(self, calls, name, params):
        self.calls = calls
        self.name = name
        self.params = params

    def execute(self):
        self.calls.append((self.name, self.params))
        return Response(
            [
                {
                    "child_id": "child-1",
                    "family_id": "family-1",
                    "invite_id": "invite-1",
                }
            ]
        )


class TableQuery:
    def __init__(self, data):
        self.data = data

    def select(self, *_fields):
        return self

    def eq(self, *_args):
        return self

    def order(self, *_args, **_kwargs):
        return self

    def maybe_single(self):
        return self

    def execute(self):
        return Response(self.data)


class FakeAdminClient:
    def __init__(self):
        self.rpc_calls = []
        self.tables = {
            "children": [
                {
                    "id": "child-1",
                    "family_id": "family-1",
                    "name": "Alice",
                    "avatar_url": None,
                    "telegram_id": 123456789,
                    "is_active": True,
                }
            ],
            "devices": [
                {
                    "id": "device-1",
                    "child_id": "child-1",
                    "device_id": "laptop-1",
                    "name": "Laptop",
                    "platform": "windows",
                    "hostname": "alice-pc",
                    "agent_version": "0.1.0",
                    "is_online": True,
                    "last_seen": "2026-09-05T09:00:00+00:00",
                }
            ],
            "time_usage": [{"used_minutes": 15}],
            "time_policies": [
                {
                    "daily_limit_minutes": 60,
                    "start_time": "08:00:00",
                    "end_time": "22:00:00",
                    "is_enabled": True,
                }
            ],
        }

    def rpc(self, name, params):
        return RpcQuery(self.rpc_calls, name, params)

    def table(self, name):
        return TableQuery(self.tables[name])


def test_register_child_uses_atomic_database_rpc():
    client = FakeAdminClient()
    service = TelegramChildService(client)

    result = service.register_child(
        telegram_id=123456789,
        invite_code="abcd-2345",
        child_name=" Alice ",
    )

    assert result == {
        "child_id": "child-1",
        "family_id": "family-1",
        "invite_id": "invite-1",
    }
    assert client.rpc_calls == [
        (
            "register_child_by_invite",
            {
                "p_code_hash": hash_invite_code("ABCD-2345"),
                "p_telegram_id": 123456789,
                "p_child_name": "Alice",
            },
        )
    ]


def test_get_dashboard_returns_child_devices_usage_and_policy():
    service = TelegramChildService(FakeAdminClient())

    result = service.get_dashboard(123456789)

    assert result["child"]["name"] == "Alice"
    assert result["devices"][0]["name"] == "Laptop"
    assert result["today_usage"] == {"used_minutes": 15}
    assert result["today_policy"]["daily_limit_minutes"] == 60


def test_register_child_rejects_empty_invite_code():
    service = TelegramChildService(FakeAdminClient())

    try:
        service.register_child(123456789, "", "Alice")
        assert False, "Empty invite code must be rejected"
    except ValueError as exc:
        assert str(exc) == "Invite code is required"


def test_register_child_rejects_empty_name():
    service = TelegramChildService(FakeAdminClient())

    try:
        service.register_child(123456789, "ABCD-2345", "   ")
        assert False, "Empty child name must be rejected"
    except ValueError as exc:
        assert str(exc) == "Child name is required"
