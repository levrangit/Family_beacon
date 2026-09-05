import asyncio

from telegram_bot.child_menu import (
    CHILD_MENU_BUTTONS,
    format_child_devices,
    format_child_profile,
    format_child_time,
)
from telegram_bot.version import get_project_version

from telegram_bot.handlers.start import (
    CHILD_INVITE_TEXT,
    CHILD_MENU_TEXT,
    CHILD_NAME_TEXT,
    CHILD_SUCCESS_TEXT,
    PARENT_MENU_BUTTONS,
    PARENT_MENU_TEXT,
    PARENT_SUCCESS_TEXT,
    handle_child_action,
    handle_parent_action,
    handle_registration_message,
    handle_role,
    handle_start,
    registration_sessions,
)


class FakeMessageEvent:
    def __init__(self, sender_id, raw_text="/start"):
        self.sender_id = sender_id
        self.raw_text = raw_text
        self.responses = []

    async def respond(self, text, buttons=None):
        self.responses.append((text, buttons))


class FakeCallbackEvent:
    def __init__(self, sender_id, data):
        self.sender_id = sender_id
        self.data = data
        self.edits = []
        self.answered = False

    async def answer(self):
        self.answered = True

    async def edit(self, text, buttons=None):
        self.edits.append((text, buttons))


class FakeBackend:
    def __init__(self):
        self.deleted = []
        self.created_invites = []
        self.registered_children = []
        self.child_dashboard = {
            "child": {
                "id": "child-1",
                "family_id": "family-1",
                "name": "Alice",
                "telegram_id": 123456,
                "is_active": True,
            },
            "devices": [
                {
                    "name": "Laptop",
                    "platform": "windows",
                    "is_online": True,
                }
            ],
            "today_usage": {"used_minutes": 15},
            "today_policy": {
                "daily_limit_minutes": 60,
                "is_enabled": True,
            },
        }

    async def lookup_telegram_id(self, telegram_id):
        return {
            "type": "profile",
            "id": "parent-1",
            "telegram_id": telegram_id,
            "role": "parent",
            "is_active": True,
        }

    async def get_child_dashboard(self, _telegram_id):
        return self.child_dashboard

    async def get_parent_profile(self, _telegram_id):
        return {
            "id": "parent-1",
            "telegram_id": 123456,
            "role": "parent",
            "is_active": True,
            "email": "parent@example.com",
        }

    async def get_parent_family(self, _telegram_id):
        return {"name": "Test family", "children": []}

    async def get_parent_children(self, _telegram_id):
        return []

    async def list_parent_invites(self, _telegram_id):
        return [
            {
                "code": "ABCD1234",
                "expires_at": "2026-09-06T01:30:00+00:00",
                "status": "active",
            }
        ]

    async def create_parent_invite(self, telegram_id):
        self.created_invites.append(telegram_id)
        return {
            "code": "ABCD1234",
            "expires_at": "2026-09-06T01:30:00+00:00",
        }

    async def register_child(self, telegram_id, invite_code, child_name):
        self.registered_children.append(
            {
                "telegram_id": telegram_id,
                "invite_code": invite_code,
                "child_name": child_name,
            }
        )
        return {
            "child_id": "child-1",
            "family_id": "family-1",
            "invite_id": "invite-1",
        }

    async def register_parent(self, **_kwargs):
        return {"user_id": "user-1"}

    async def delete_parent_account(self, telegram_id):
        self.deleted.append(telegram_id)
        return {"status": "deleted"}


def teardown_function(_function):
    registration_sessions.clear()


def test_registered_parent_start_shows_all_parent_actions():
    event = FakeMessageEvent(123456)
    backend = FakeBackend()

    asyncio.run(handle_start(event, backend))

    text, buttons = event.responses[0]
    assert text == PARENT_MENU_TEXT
    assert text == f"🌟 Семейный маяк · {get_project_version()}"
    labels = [button.text for row in buttons for button in row]
    assert labels == [
        "🏠 Семья",
        "👤 Профиль",
        "👶 Дети",
        "📨 Приглашения",
        "🗑 Забыть меня",
    ]
    assert buttons == PARENT_MENU_BUTTONS


def test_registered_child_start_shows_child_menu():
    event = FakeMessageEvent(123456)
    backend = FakeBackend()
    backend.child_dashboard["child"]["name"] = "Мария"

    async def child_lookup(_telegram_id):
        return {
            "type": "child",
            **backend.child_dashboard["child"],
        }

    backend.lookup_telegram_id = child_lookup

    asyncio.run(handle_start(event, backend))

    text, buttons = event.responses[0]
    assert "🌟 Семейный маяк" in text
    assert "Привет, Мария!" in text
    assert [button.text for row in buttons for button in row] == [
        button.text for row in CHILD_MENU_BUTTONS for button in row
    ]
    assert "🔄 Обновить" not in text


def test_child_menu_loads_dashboard_without_refresh_button():
    event = FakeCallbackEvent(123456, b"child:menu")
    backend = FakeBackend()

    asyncio.run(handle_child_action(event, backend))

    assert event.answered is True
    text, buttons = event.edits[0]
    assert "Привет, Alice!" in text
    assert "🌟 Семейный маяк" in text
    assert buttons == CHILD_MENU_BUTTONS
    assert [button.text for row in buttons for button in row] == [
        "👤 Профиль",
        "⏱ Время",
        "💻 Устройства",
    ]


def test_child_profile_action_returns_profile_information():
    event = FakeCallbackEvent(123456, b"child:profile")
    backend = FakeBackend()

    asyncio.run(handle_child_action(event, backend))

    text, buttons = event.edits[0]
    assert text == format_child_profile(backend.child_dashboard["child"])
    assert "Telegram ID:" not in text
    assert "123456" not in text
    assert buttons[0][0].text == "◀️ Назад"


def test_child_time_action_returns_usage_and_limit():
    event = FakeCallbackEvent(123456, b"child:time")
    backend = FakeBackend()

    asyncio.run(handle_child_action(event, backend))

    text, _buttons = event.edits[0]
    assert text == format_child_time(backend.child_dashboard)
    assert "Использовано сегодня: 15 мин." in text
    assert "Лимит сегодня: 60 мин." in text
    assert "Осталось: 45 мин." in text


def test_child_devices_action_returns_devices():
    event = FakeCallbackEvent(123456, b"child:devices")
    backend = FakeBackend()

    asyncio.run(handle_child_action(event, backend))

    text, _buttons = event.edits[0]
    assert text == format_child_devices(backend.child_dashboard)
    assert "Laptop" in text
    assert "онлайн" in text


def test_profile_action_returns_profile_information():
    event = FakeCallbackEvent(123456, b"parent:profile")
    backend = FakeBackend()

    asyncio.run(handle_parent_action(event, backend))

    assert event.answered is True
    text, _buttons = event.edits[0]
    assert "👤 Профиль" in text
    assert "Мой профиль" not in text
    assert "parent@example.com" in text
    assert "Telegram ID:" not in text
    assert "123456" not in text


def test_invites_action_returns_codes_and_expiration():
    event = FakeCallbackEvent(123456, b"parent:invites")
    backend = FakeBackend()

    asyncio.run(handle_parent_action(event, backend))

    assert event.answered is True
    text, buttons = event.edits[0]
    assert "📨 Приглашения" in text
    assert "Мои приглашения" not in text
    assert "Код: ABCD1234" in text
    assert "Действует до: 06.09.2026" in text
    assert buttons[0][0].text == "➕ Выдать приглашение"
    assert buttons[1][0].text == "◀️ Назад"


def test_create_invite_action_returns_code_and_expiration():
    event = FakeCallbackEvent(123456, b"parent:create_invite")
    backend = FakeBackend()

    asyncio.run(handle_parent_action(event, backend))

    assert event.answered is True
    assert backend.created_invites == [123456]

    text, buttons = event.edits[0]
    assert "🎟 Приглашение создано!" in text
    assert "Код: ABCD1234" in text
    assert "Действительно до: 06.09.2026" in text
    assert "Передайте этот код ребёнку." in text
    assert buttons[0][0].text == "➕ Выдать приглашение"
    assert buttons[1][0].text == "◀️ Назад"


def test_child_role_starts_invite_registration():
    event = FakeCallbackEvent(123456, b"role:child")

    asyncio.run(handle_role(event))

    assert event.answered is True
    assert event.edits[0][0] == CHILD_INVITE_TEXT
    assert registration_sessions[123456].role == "child"
    assert registration_sessions[123456].state == "waiting_invite_code"


def test_child_registration_asks_for_name_after_invite_code():
    session_event = FakeCallbackEvent(123456, b"role:child")
    asyncio.run(handle_role(session_event))

    event = FakeMessageEvent(123456, "ABCD-2345")
    backend = FakeBackend()
    asyncio.run(handle_registration_message(event, backend))

    assert event.responses == [(CHILD_NAME_TEXT, None)]
    assert registration_sessions[123456].invite_code == "ABCD-2345"
    assert registration_sessions[123456].state == "waiting_child_name"


def test_child_registration_completes_and_shows_menu():
    session_event = FakeCallbackEvent(123456, b"role:child")
    asyncio.run(handle_role(session_event))

    code_event = FakeMessageEvent(123456, "abcd-2345")
    backend = FakeBackend()
    asyncio.run(handle_registration_message(code_event, backend))

    name_event = FakeMessageEvent(123456, " Alice ")
    asyncio.run(handle_registration_message(name_event, backend))

    assert backend.registered_children == [
        {
            "telegram_id": 123456,
            "invite_code": "ABCD-2345",
            "child_name": "Alice",
        }
    ]
    assert name_event.responses == [
        (CHILD_SUCCESS_TEXT, None),
        (CHILD_MENU_TEXT, CHILD_MENU_BUTTONS),
    ]
    assert 123456 not in registration_sessions


def test_parent_registration_completes_and_shows_menu():
    session_event = FakeCallbackEvent(123456, b"role:parent")
    asyncio.run(handle_role(session_event))

    login_event = FakeMessageEvent(123456, "parent@example.com")
    backend = FakeBackend()
    asyncio.run(handle_registration_message(login_event, backend))

    password_event = FakeMessageEvent(123456, "SecretPassword123")
    asyncio.run(handle_registration_message(password_event, backend))

    assert password_event.responses == [
        (PARENT_SUCCESS_TEXT, None),
        (PARENT_MENU_TEXT, PARENT_MENU_BUTTONS),
    ]
    assert 123456 not in registration_sessions


def test_forget_confirmation_deletes_account_after_confirmation():
    backend = FakeBackend()

    confirm_event = FakeCallbackEvent(123456, b"parent:forget")
    asyncio.run(handle_parent_action(confirm_event, backend))
    text, buttons = confirm_event.edits[0]
    assert "Это действие необратимо" in text
    assert buttons[1][0].text == "🗑 Да, удалить всё"

    delete_event = FakeCallbackEvent(123456, b"parent:forget:confirm")
    asyncio.run(handle_parent_action(delete_event, backend))

    assert backend.deleted == [123456]
    assert "Все данные" in delete_event.edits[0][0]
