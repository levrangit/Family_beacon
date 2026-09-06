import asyncio

from telegram_bot.family_rename_handlers import (
    FAMILY_RENAME_SUCCESS_BUTTONS,
    handle_family_rename_message,
)
from telegram_bot.handlers.start import family_rename_sessions


class FakeMessageEvent:
    def __init__(self, sender_id, raw_text):
        self.sender_id = sender_id
        self.raw_text = raw_text
        self.responses = []

    async def respond(self, text, buttons=None):
        self.responses.append((text, buttons))


class FakeBackend:
    def __init__(self):
        self.family = {"id": "family-1", "name": "Моя семья"}

    async def rename_parent_family(self, _telegram_id, name):
        self.family["name"] = name.strip()
        return self.family


def teardown_function(_function):
    family_rename_sessions.clear()


def test_family_rename_success_shows_back_button_to_family_menu():
    family_rename_sessions.add(123456)
    event = FakeMessageEvent(123456, "  Леопольдовы  ")
    backend = FakeBackend()

    handled = asyncio.run(handle_family_rename_message(event, backend))

    assert handled is True
    assert event.responses == [
        (
            "✅ Название семьи изменено.\n\nНовое название:\nЛеопольдовы",
            FAMILY_RENAME_SUCCESS_BUTTONS,
        )
    ]
    assert FAMILY_RENAME_SUCCESS_BUTTONS[0][0].text == "◀️ Назад"
    assert 123456 not in family_rename_sessions


def test_non_rename_message_is_not_handled():
    event = FakeMessageEvent(123456, "Леопольдовы")
    backend = FakeBackend()

    handled = asyncio.run(handle_family_rename_message(event, backend))

    assert handled is False
    assert event.responses == []
