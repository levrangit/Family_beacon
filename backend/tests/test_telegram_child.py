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


class FakeAdminClient:
    def __init__(self):
        self.rpc_calls = []

    def rpc(self, name, params):
        return RpcQuery(self.rpc_calls, name, params)


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
