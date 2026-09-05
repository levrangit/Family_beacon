import asyncio

from telegram_bot.handlers.start import (
    FAMILY_RENAME_TEXT,
    FAMILY_RENAME_BUTTONS,
    handle_parent_action,
    handle_registration_message,
    family_rename_sessions,
)


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


class FakeMessageEvent:
    def __init__(self, sender_id, raw_text):
        self.sender_id = sender_id
        self.raw_text = raw_text
        self.responses = []

    async def respond(self, text, buttons=None):
        self.responses.append((text, buttons))


class FakeBackend:
    def __init__(self):
        self.family = {
            "id": "family-1",
            "name": "Моя семья",
            "children": [
                {"id": "child-1", "name": "Мария", "is_active": True},
                {"id": "child-2", "name": "Иван", "is_active": True},
            ],
        }
        self.dashboard = {
            "child": {
                "id": "child-1",
                "family_id": "family-1",
                "name": "Мария",
                "is_active": True,
            },
            "devices": [{"name": "Laptop", "platform": "windows", "is_online": True}],
            "today_usage": {"used_minutes": 15},
            "today_policy": {"daily_limit_minutes": 60, "is_enabled": True},
        }

    async def get_parent_family(self, _telegram_id):
        return self.family

    async def rename_parent_family(self, _telegram_id, name):
        self.family["name"] = name.strip()
        return {"id": self.family["id"], "name": self.family["name"]}

    async def get_parent_child_dashboard(self, _telegram_id, child_id):
        if child_id != self.dashboard["child"]["id"]:
            raise ValueError("Child not found")
        return self.dashboard


def teardown_function(_function):
    family_rename_sessions.clear()


def test_family_menu_shows_children_as_buttons_and_family_name_as_button():
    event = FakeCallbackEvent(123456, b"parent:family")
    backend = FakeBackend()

    asyncio.run(handle_parent_action(event, backend))

    text, buttons = event.edits[0]
    assert text == "🏠 Семья"
    assert "🏠 Моя семья" in buttons[0][0].text
    assert [button.text for row in buttons[1:3] for button in row] == ["👶 Мария", "👶 Иван"]
    assert buttons[-2][0].text == "➕ Выдать приглашение"
    assert buttons[-1][0].text == "◀️ Назад"


def test_family_menu_without_children_shows_not_registered_message():
    event = FakeCallbackEvent(123456, b"parent:family")
    backend = FakeBackend()
    backend.family["children"] = []

    asyncio.run(handle_parent_action(event, backend))

    text, buttons = event.edits[0]
    assert text == "🏠 Семья\n\nДети не зарегистрированы."
    assert buttons[-2][0].text == "➕ Выдать приглашение"
    assert buttons[-1][0].text == "◀️ Назад"


def test_family_name_button_opens_rename_prompt():
    event = FakeCallbackEvent(123456, b"parent:family:rename")
    backend = FakeBackend()

    asyncio.run(handle_parent_action(event, backend))

    text, buttons = event.edits[0]
    assert "Текущее название:" in text
    assert "Моя семья" in text
    assert "Введите новое название семьи:" in text
    assert buttons == FAMILY_RENAME_BUTTONS
    assert 123456 in family_rename_sessions


def test_family_rename_updates_name_and_returns_to_family_menu():
    family_rename_sessions.add(123456)
    event = FakeMessageEvent(123456, "  Семья Леопольдовых  ")
    backend = FakeBackend()

    asyncio.run(handle_registration_message(event, backend))

    assert "Семья Леопольдовых" in event.responses[0][0]
    assert event.responses[1][0] == ""
    assert "🏠 Семья Леопольдовых" in event.responses[1][1][0][0].text
    assert 123456 not in family_rename_sessions


def test_child_button_opens_child_menu():
    event = FakeCallbackEvent(123456, b"parent:family:child:child-1")
    backend = FakeBackend()

    asyncio.run(handle_parent_action(event, backend))

    text, buttons = event.edits[0]
    assert text == "👶 Мария"
    assert [button.text for row in buttons for button in row] == [
        "👤 Мой профиль",
        "⏱ Моё время",
        "💻 Мои устройства",
        "◀️ Назад",
    ]


def test_parent_child_time_loads_fresh_dashboard():
    event = FakeCallbackEvent(123456, b"parent:child:child-1:time")
    backend = FakeBackend()

    asyncio.run(handle_parent_action(event, backend))

    text, buttons = event.edits[0]
    assert "Мария — время" in text
    assert "Использовано сегодня: 15 мин." in text
    assert "Лимит сегодня: 60 мин." in text
    assert buttons[0][0].text == "◀️ Назад"
