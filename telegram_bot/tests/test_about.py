import asyncio

from telegram_bot.about import ABOUT_BUTTONS, ABOUT_TEXT, handle_about_action


class FakeSender:
    username = "test_user"


class FakeClient:
    def __init__(self):
        self.messages = []

    async def send_message(self, telegram_id, text):
        self.messages.append((telegram_id, text))


class FakeCallbackEvent:
    def __init__(self, sender_id, data, client=None):
        self.sender_id = sender_id
        self.data = data
        self.client = client or FakeClient()
        self.edits = []
        self.answered = False

    async def answer(self):
        self.answered = True

    async def edit(self, text, buttons=None):
        self.edits.append((text, buttons))

    async def get_sender(self):
        return FakeSender()


def test_about_action_shows_description():
    event = FakeCallbackEvent(123456, b"parent:about")

    asyncio.run(handle_about_action(event))

    assert event.answered is True
    text, buttons = event.edits[0]
    assert text == ABOUT_TEXT
    assert buttons == ABOUT_BUTTONS


def test_thanks_action_sends_message_to_author(monkeypatch):
    monkeypatch.setenv("AUTHOR_TELEGRAM_ID", "987654321")
    client = FakeClient()
    event = FakeCallbackEvent(123456, b"parent:about:thanks", client)

    asyncio.run(handle_about_action(event))

    assert event.answered is True
    assert client.messages == [
        (987654321, '💌 Пользователь @test_user сказал вам «Спасибо!»')
    ]
    assert event.edits[0][0] == "❤️ Спасибо! Ваше сообщение отправлено автору."
    assert event.edits[0][1] == ABOUT_BUTTONS


def test_thanks_action_reports_unconfigured_author(monkeypatch):
    monkeypatch.delenv("AUTHOR_TELEGRAM_ID", raising=False)
    event = FakeCallbackEvent(123456, b"parent:about:thanks")

    asyncio.run(handle_about_action(event))

    assert event.edits[0][0] == "❌ Благодарность пока не настроена."
    assert event.edits[0][1] == ABOUT_BUTTONS
    assert event.client.messages == []
