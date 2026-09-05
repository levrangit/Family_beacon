from datetime import datetime, timezone

from app.telegram_parent import TelegramParentService


class Response:
    def __init__(self, data):
        self.data = data


class Query:
    def __init__(self, rows):
        self.rows = rows
        self.payload = None

    def select(self, *_args):
        return self

    def eq(self, key, value):
        self.rows = [row for row in self.rows if row.get(key) == value]
        return self

    def order(self, *_args, **_kwargs):
        return self

    def limit(self, *_args):
        return self

    def update(self, payload):
        self.payload = payload
        for row in self.rows:
            row.update(payload)
        return self

    def execute(self):
        return Response(self.rows)


class FakeAdminClient:
    def __init__(self, tables):
        self.tables = tables

    def table(self, name):
        return Query(self.tables.setdefault(name, []))


def tables():
    now = datetime.now(timezone.utc).isoformat()
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
                "created_at": now,
            }
        ],
        "families": [
            {
                "id": "family-1",
                "name": "Моя семья",
                "created_at": now,
                "updated_at": now,
            }
        ],
        "children": [
            {
                "id": "child-1",
                "family_id": "family-1",
                "name": "Мария",
                "avatar_url": None,
                "telegram_id": 777,
                "is_active": True,
            }
        ],
        "devices": [
            {
                "id": "device-1",
                "child_id": "child-1",
                "device_id": "pc-1",
                "name": "Laptop",
                "platform": "windows",
                "hostname": "MARY-PC",
                "agent_version": "1.0",
                "is_online": True,
                "last_seen": now,
            }
        ],
        "time_usage": [
            {"child_id": "child-1", "usage_date": datetime.now(timezone.utc).date().isoformat(), "used_minutes": 15}
        ],
        "time_policies": [
            {
                "child_id": "child-1",
                "day_of_week": (datetime.now(timezone.utc).weekday() + 1) % 7,
                "daily_limit_minutes": 60,
                "start_time": None,
                "end_time": None,
                "is_enabled": True,
            }
        ],
    }


def test_rename_family_updates_name_without_schema_change():
    data = tables()
    service = TelegramParentService(FakeAdminClient(data))

    result = service.rename_family(123456, "  Семья Леопольдовых  ")

    assert result == {"id": "family-1", "name": "Семья Леопольдовых"}
    assert data["families"][0]["name"] == "Семья Леопольдовых"


def test_rename_family_rejects_empty_name():
    service = TelegramParentService(FakeAdminClient(tables()))

    try:
        service.rename_family(123456, "   ")
    except ValueError as exc:
        assert str(exc) == "Family name is required"
    else:
        raise AssertionError("Expected empty family name to be rejected")


def test_get_child_dashboard_is_limited_to_parent_family():
    service = TelegramParentService(FakeAdminClient(tables()))

    result = service.get_child_dashboard(123456, "child-1")

    assert result["child"]["name"] == "Мария"
    assert result["devices"][0]["name"] == "Laptop"
    assert result["today_usage"] == {"used_minutes": 15}
    assert result["today_policy"]["daily_limit_minutes"] == 60


def test_get_child_dashboard_rejects_child_from_another_family():
    data = tables()
    data["children"].append(
        {
            "id": "child-2",
            "family_id": "another-family",
            "name": "Чужой ребёнок",
            "avatar_url": None,
            "telegram_id": 888,
            "is_active": True,
        }
    )
    service = TelegramParentService(FakeAdminClient(data))

    try:
        service.get_child_dashboard(123456, "child-2")
    except ValueError as exc:
        assert str(exc) == "Child not found"
    else:
        raise AssertionError("Expected child from another family to be rejected")
