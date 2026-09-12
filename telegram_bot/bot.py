from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path

from telegram_bot.device_registration_handlers import (
    handle_device_registration_action,
    handle_device_registration_message,
)
from telegram_bot.family_rename_handlers import handle_family_rename_message
from telegram_bot.agent_installation_handlers import (
    handle_agent_installation_action,
    parent_family_buttons_with_installation,
)

from telethon import TelegramClient, events

from telegram_bot.backend_client import BackendClient
from telegram_bot.config import (
    API_HASH,
    API_ID,
    BACKEND_URL,
    BOT_TOKEN,
    SESSION_PATH,
    TELEGRAM_BOT_SHARED_SECRET,
)
from telegram_bot.handlers.start import (
    handle_child_action,
    handle_parent_action as handle_parent_action_base,
    handle_registration_message,
    handle_role,
    handle_start,
    registration_sessions,
)
from telegram_bot.speech_to_text import load_model, transcribe_audio


client = TelegramClient(SESSION_PATH, API_ID, API_HASH)
backend = BackendClient(BACKEND_URL, TELEGRAM_BOT_SHARED_SECRET)


class _TextEventAdapter:
    """Expose recognized voice text through the existing message-handler interface."""

    def __init__(self, event: events.NewMessage.Event, text: str) -> None:
        self._event = event
        self.sender_id = event.sender_id
        self.raw_text = text

    async def respond(self, *args, **kwargs):
        return await self._event.respond(*args, **kwargs)


@client.on(events.NewMessage(pattern=r"^/start(?:@\w+)?$"))
async def start_handler(event: events.NewMessage.Event) -> None:
    await handle_start(event, backend)


@client.on(events.NewMessage())
async def voice_message_handler(event: events.NewMessage.Event) -> None:
    if not event.message or not event.message.voice:
        return

    try:
        with tempfile.TemporaryDirectory(prefix="family_beacon_voice_") as temp_dir:
            audio_path = Path(temp_dir) / "voice.ogg"
            await event.message.download_media(file=str(audio_path))
            text = await asyncio.to_thread(transcribe_audio, audio_path)

        if not text:
            await event.respond("❌ Не удалось распознать голосовое сообщение.\n\nПопробуйте ещё раз.")
            return

        text_event = _TextEventAdapter(event, text)
        if await handle_device_registration_message(text_event, backend, registration_sessions):
            return
        if await handle_family_rename_message(text_event, backend):
            return
        await handle_registration_message(text_event, backend)
    except Exception:
        await event.respond(
            "❌ Не удалось обработать голосовое сообщение.\n\n"
            "Попробуйте ещё раз позже.",
        )


@client.on(events.NewMessage())
async def registration_message_handler(event: events.NewMessage.Event) -> None:
    if event.message and event.message.voice:
        return
    if event.raw_text and event.raw_text.startswith("/"):
        return
    if await handle_device_registration_message(event, backend, registration_sessions):
        return
    if await handle_family_rename_message(event, backend):
        return
    await handle_registration_message(event, backend)


@client.on(events.CallbackQuery(data=b"role:parent"))
async def parent_role_handler(event: events.CallbackQuery.Event) -> None:
    await handle_role(event)


@client.on(events.CallbackQuery(data=b"role:child"))
async def child_role_handler(event: events.CallbackQuery.Event) -> None:
    await handle_role(event)


@client.on(events.CallbackQuery(pattern=r"^parent:"))
async def parent_action_handler(event: events.CallbackQuery.Event) -> None:
    await handle_parent_action_base(event, backend)


@client.on(events.CallbackQuery(data=b"parent:agent_installation"))
async def parent_agent_installation_handler(event: events.CallbackQuery.Event) -> None:
    await handle_agent_installation_action(event, backend)


@client.on(events.CallbackQuery(data=b"parent:family"))
async def parent_family_installation_button_handler(event: events.CallbackQuery.Event) -> None:
    telegram_id = event.sender_id
    if telegram_id is None:
        return
    try:
        family = await backend.get_parent_family(telegram_id)
    except Exception:
        return
    children = family.get("children") or []
    text = "🏠 Семья" if children else "🏠 Семья\n\nДети не зарегистрированы."
    await event.edit(text, buttons=parent_family_buttons_with_installation(family))


@client.on(events.CallbackQuery(data=b"parent:family:rename:cancel"))
async def parent_family_rename_cancel_installation_button_handler(
    event: events.CallbackQuery.Event,
) -> None:
    telegram_id = event.sender_id
    if telegram_id is None:
        return
    try:
        family = await backend.get_parent_family(telegram_id)
    except Exception:
        return
    children = family.get("children") or []
    text = "🏠 Семья" if children else "🏠 Семья\n\nДети не зарегистрированы."
    await event.edit(text, buttons=parent_family_buttons_with_installation(family))


@client.on(events.CallbackQuery(
    pattern=r"^child:(?:device_(?:register|registration_back)|devices_menu)$"
))
async def child_device_registration_action_handler(event: events.CallbackQuery.Event) -> None:
    await handle_device_registration_action(event, backend, registration_sessions)


@client.on(events.CallbackQuery(pattern=r"^child:"))
async def child_action_handler(event: events.CallbackQuery.Event) -> None:
    await handle_child_action(event, backend)


async def main() -> None:
    await asyncio.to_thread(load_model)
    await client.start(bot_token=BOT_TOKEN)
    print("Family Beacon Telegram bot started")
    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
