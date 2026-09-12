import os

os.environ.setdefault("TELEGRAM_API_ID", "1")
os.environ.setdefault("TELEGRAM_API_HASH", "test-api-hash")
os.environ.setdefault("TELEGRAM_BOT_TOKEN", "test-bot-token")
os.environ.setdefault("TELEGRAM_BOT_SHARED_SECRET", "test-shared-secret")

import pytest

from telegram_bot import bot


class FakeVoiceMessage:
    voice = True

    async def download_media(self, file):
        with open(file, "wb") as output:
            output.write(b"fake audio")
        return file


class FakeTextMessage:
    voice = False


class FakeEvent:
    sender_id = 123456789

    def __init__(self, message):
        self.message = message
        self.raw_text = ""
        self.responses = []

    async def respond(self, *args, **kwargs):
        self.responses.append((args, kwargs))


@pytest.mark.asyncio
async def test_voice_message_is_transcribed_and_sent_to_existing_message_flow(monkeypatch):
    event = FakeEvent(FakeVoiceMessage())
    seen = []

    async def fake_device_handler(event, backend, sessions):
        return False

    async def fake_family_handler(event, backend):
        return False

    async def fake_registration_handler(event, backend):
        seen.append(event.raw_text)

    monkeypatch.setattr(bot, "transcribe_audio", lambda path: " ABCD-2345 ")
    monkeypatch.setattr(bot, "handle_device_registration_message", fake_device_handler)
    monkeypatch.setattr(bot, "handle_family_rename_message", fake_family_handler)
    monkeypatch.setattr(bot, "handle_registration_message", fake_registration_handler)

    await bot.voice_message_handler(event)

    assert seen == [" ABCD-2345 "]
    assert event.responses == []


@pytest.mark.asyncio
async def test_text_message_handler_ignores_voice_message(monkeypatch):
    event = FakeEvent(FakeVoiceMessage())

    async def unexpected_handler(*args, **kwargs):
        raise AssertionError("voice message reached the text handler")

    monkeypatch.setattr(bot, "handle_device_registration_message", unexpected_handler)
    monkeypatch.setattr(bot, "handle_family_rename_message", unexpected_handler)
    monkeypatch.setattr(bot, "handle_registration_message", unexpected_handler)

    await bot.registration_message_handler(event)

    assert event.responses == []


@pytest.mark.asyncio
async def test_voice_message_reports_empty_transcription(monkeypatch):
    event = FakeEvent(FakeVoiceMessage())

    monkeypatch.setattr(bot, "transcribe_audio", lambda path: "")

    await bot.voice_message_handler(event)

    assert len(event.responses) == 1
    assert "Не удалось распознать" in event.responses[0][0][0]
