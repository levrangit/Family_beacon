import asyncio

from telegram_bot.handlers.start import handle_parent_action, handle_start


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

    async def delete_parent_account(self, telegram_id):
        self.deleted.append(telegram_id)
        return {"status": "deleted"}


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
