import asyncio

from telegram_bot.handlers.start import (
    CHILD_INVITE_TEXT,
    CHILD_NAME_TEXT,
    CHILD_SUCCESS_TEXT,
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

    async def lookup_telegram_id(self, telegram_id):
        return {
            "type": "profile",
            "id": "parent-1",
            "telegram_id": telegram_id,
            "role": "parent",
            "is_active": True,
        }

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
    assert "Family Beacon" in text
    labels = [button.text for row in buttons for button in row]
    assert labels == [
        "🏠 Моя семья",
        "👤 Мой профиль",
        "👶 Дети",
        "📨 Мои приглашения",
        "➕ Выдать приглашение ребенку",
        "🗑 Забыть меня",
    ]


def test_profile_action_returns_profile_information():
    event = FakeCallbackEvent(123456, b"parent:profile")
    backend = FakeBackend()

    asyncio.run(handle_parent_action(event, backend))

    assert event.answered is True
    text, _buttons = event.edits[0]
    assert "Мой профиль" in text
    assert "parent@example.com" in text
    assert "123456" in text


def test_invites_action_returns_codes_and_expiration():
    event = FakeCallbackEvent(123456, b"parent:invites")
    backend = FakeBackend()

    asyncio.run(handle_parent_action(event, backend))

    assert event.answered is True
    text, buttons = event.edits[0]
    assert "📨 Мои приглашения" in text
    assert "Код: ABCD1234" in text
    assert "Действует до: 06.09.2026" in text
    assert buttons[0][0].text == "◀️ Назад"


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
    assert buttons[0][0].text == "◀️ Назад"


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


def test_child_registration_completes_and_calls_backend():
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
    assert name_event.responses == [(CHILD_SUCCESS_TEXT, None)]
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
