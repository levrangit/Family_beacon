from __future__ import annotations

from telegram_bot.device_registration_handlers import (
    handle_device_registration_action,
    handle_device_registration_message,
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
    handle_parent_action,
    handle_registration_message,
    handle_role,
    handle_start,
    registration_sessions,
)


client = TelegramClient(SESSION_PATH, API_ID, API_HASH)
backend = BackendClient(BACKEND_URL, TELEGRAM_BOT_SHARED_SECRET)


@client.on(events.NewMessage(pattern=r"^/start(?:@\w+)?$"))
async def start_handler(event: events.NewMessage.Event) -> None:
    await handle_start(event, backend)


@client.on(events.NewMessage())
async def registration_message_handler(event: events.NewMessage.Event) -> None:
    if event.raw_text and event.raw_text.startswith("/"):
        return
    if await handle_device_registration_message(event, backend, registration_sessions):
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
    await handle_parent_action(event, backend)


@client.on(events.CallbackQuery(pattern=r"^child:device_(?:register)$|^child:devices_menu$"))
async def child_device_registration_action_handler(event: events.CallbackQuery.Event) -> None:
    await handle_device_registration_action(event, backend, registration_sessions)


@client.on(events.CallbackQuery(pattern=r"^child:"))
async def child_action_handler(event: events.CallbackQuery.Event) -> None:
    await handle_child_action(event, backend)


async def main() -> None:
    await client.start(bot_token=BOT_TOKEN)
    print("Family Beacon Telegram bot started")
    await client.run_until_disconnected()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
