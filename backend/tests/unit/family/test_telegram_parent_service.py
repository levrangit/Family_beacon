from datetime import datetime, timedelta, timezone

from app.telegram_parent import TelegramParentService


class Response:
    def __init__(self, data):
        self.data = data


class TableQuery:
    def __init__(self, rows):
        self.rows = rows

    def select(self, *_args):
        return self

    def eq(self, key, value):
        self.rows = [row for row in self.rows if row.get(key) == value]
        return self

    def order(self, *_args, **_kwargs):
        return self

    def limit(self, *_args):
        return self

    def execute(self):
        return Response(self.rows)


class InsertQuery:
    def __init__(self, rows, payload):
        self.rows = rows
        self.payload = payload

    def execute(self):
        row = dict(self.payload)
        if "id" not in row:
            row["id"] = f"{len(self.rows) + 1}"
        self.rows.append(row)
        return Response([row])


class FakeAuthAdmin:
    def __init__(self):
        self.deleted_user_ids = []

    def delete_user(self, user_id):
        self.deleted_user_ids.append(user_id)


class FakeAuth:
    def __init__(self):
        self.admin = FakeAuthAdmin()


class FakeAdminClient:
    def __init__(self, tables):
        self.tables = tables
        self.auth = FakeAuth()
        self.rpc_calls = []

    def table(self, name):
        return TableQuery(self.tables.setdefault(name, []))

    def insert(self, name, payload):
        return InsertQuery(self.tables.setdefault(name, []), payload)

    def rpc(self, name, params):
        self.rpc_calls.append((name, params))
        return TableQuery([{}])


class TableAwareFakeAdminClient(FakeAdminClient):
    def table(self, name):
        rows = self.tables.setdefault(name, [])
        query = TableQuery(rows)
        query.insert = lambda payload: InsertQuery(rows, payload)
        return query


def parent_tables():
    return {
        "profiles": [
            {
                "id": "parent-1",
                "display_name": "Parent",
                "telegram_id": 123456,
                "role": "parent",
                "is_active": True,
            }
        ],
        "family_members": [
            {
                "profile_id": "parent-1",
                "family_id": "family-1",
                "member_type": "parent",
                "created_at": "2026-09-05T10:00:00+00:00",
            }
        ],
        "families": [
            {
                "id": "family-1",
                "name": "Test family",
                "created_at": "2026-09-05T10:00:00+00:00",
                "updated_at": "2026-09-05T10:00:00+00:00",
            }
        ],
        "children": [
            {
                "id": "child-1",
                "name": "Child",
                "avatar_url": None,
                "is_active": True,
                "created_at": "2026-09-05T10:00:00+00:00",
                "updated_at": "2026-09-05T10:00:00+00:00",
                "family_id": "family-1",
            }
        ],
    }


def test_get_family_returns_family_and_children():
    service = TelegramParentService(FakeAdminClient(parent_tables()))

    result = service.get_family(123456)

    assert result["id"] == "family-1"
    assert result["name"] == "Test family"
    assert result["children"][0]["name"] == "Child"


def test_list_invites_reports_active_used_expired_and_revoked():
    now = datetime.now(timezone.utc)
    tables = parent_tables()
    tables["family_invites"] = [
        {
            "id": "active",
            "family_id": "family-1",
            "created_by": "parent-1",
            "code": "ACTIVE123",
            "expires_at": (now + timedelta(hours=1)).isoformat(),
            "used_at": None,
            "used_by": None,
            "revoked_at": None,
            "created_at": now.isoformat(),
        },
        {
            "id": "used",
            "family_id": "family-1",
            "created_by": "parent-1",
            "code": "USED1234",
            "expires_at": (now + timedelta(hours=1)).isoformat(),
            "used_at": now.isoformat(),
            "used_by": "child-profile",
            "revoked_at": None,
            "created_at": now.isoformat(),
        },
        {
            "id": "expired",
            "family_id": "family-1",
            "created_by": "parent-1",
            "code": "EXPIRED1",
            "expires_at": (now - timedelta(hours=1)).isoformat(),
            "used_at": None,
            "used_by": None,
            "revoked_at": None,
            "created_at": now.isoformat(),
        },
        {
            "id": "revoked",
            "family_id": "family-1",
            "created_by": "parent-1",
            "code": "REVOKED1",
            "expires_at": (now + timedelta(hours=1)).isoformat(),
            "used_at": None,
            "used_by": None,
            "revoked_at": now.isoformat(),
            "created_at": now.isoformat(),
        },
    ]
    service = TelegramParentService(FakeAdminClient(tables))

    result = service.list_invites(123456)
    statuses = {item["invite_id"]: item["status"] for item in result}
    codes = {item["invite_id"]: item["code"] for item in result}

    assert statuses == {
        "active": "active",
        "used": "used",
        "expired": "expired",
        "revoked": "revoked",
    }
    assert codes == {
        "active": "ACTIVE123",
        "used": "USED1234",
        "expired": "EXPIRED1",
        "revoked": "REVOKED1",
    }


def test_create_child_invite_uses_existing_family():
    tables = parent_tables()
    tables["family_invites"] = []
    client = TableAwareFakeAdminClient(tables)
    service = TelegramParentService(client)

    result = service.create_child_invite(123456)

    assert result["invite_id"] == "1"
    assert result["code"]
    assert result["expires_at"]
    assert tables["family_invites"][0]["family_id"] == "family-1"
    assert tables["family_invites"][0]["created_by"] == "parent-1"
    assert tables["family_invites"][0]["code"] == result["code"]
    assert tables["family_invites"][0]["code_hash"]


def test_create_child_invite_creates_family_when_parent_has_none():
    tables = parent_tables()
    tables["family_members"] = []
    tables["families"] = []
    tables["family_invites"] = []
    client = TableAwareFakeAdminClient(tables)
    service = TelegramParentService(client)

    result = service.create_child_invite(123456)

    assert result["code"]
    assert result["expires_at"]
    assert len(tables["families"]) == 1
    assert tables["families"][0]["name"] == "Моя семья"
    assert tables["family_members"] == [
        {
            "family_id": "1",
            "profile_id": "parent-1",
            "member_type": "parent",
            "id": "1",
        }
    ]
    assert tables["family_invites"][0]["family_id"] == "1"
    assert tables["family_invites"][0]["created_by"] == "parent-1"
    assert tables["family_invites"][0]["code"] == result["code"]


def test_delete_parent_account_calls_database_rpc_and_auth_delete():
    client = FakeAdminClient(parent_tables())
    service = TelegramParentService(client)

    result = service.delete_parent_account(123456)

    assert result == {"status": "deleted"}
    assert client.rpc_calls == [
        ("delete_parent_account", {"p_profile_id": "parent-1"})
    ]
    assert client.auth.admin.deleted_user_ids == ["parent-1"]


def test_non_parent_profile_is_rejected():
    tables = parent_tables()
    tables["profiles"][0]["role"] = "admin"
    service = TelegramParentService(FakeAdminClient(tables))

    try:
        service.get_family(123456)
    except ValueError as exc:
        assert str(exc) == "Telegram account is not an active parent"
    else:
        raise AssertionError("Expected non-parent profile to be rejected")
