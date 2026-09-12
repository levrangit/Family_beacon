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
from tgnet.connection import TgNetConnection
from tgnet.connection.faketls import TgNetConnectionTls

from telegram_bot.backend_client import BackendClient
from telegram_bot.config import (
    API_HASH,
    API_ID,
    BACKEND_URL,
    BOT_TOKEN,
    MT_PROXY_HOST,
    MT_PROXY_PORT,
    MT_PROXY_SECRET,
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


class _FakeTlsProxyConnection(TgNetConnectionTls):
    """Adapt Telethon's proxy tuple to tgnet's FakeTLS connection API."""

    def __init__(
        self,
        ip,
        port,
        dc_id,
        *,
        loggers,
        proxy=None,
        local_addr=None,
        **kwargs,
    ):
        if not proxy or len(proxy) < 3:
            raise ValueError("FakeTLS MTProto proxy requires host, port and secret")

        proxy_host, proxy_port, proxy_secret = proxy[:3]
        if isinstance(proxy_secret, str):
            proxy_secret = bytes.fromhex(proxy_secret)

        super().__init__(
            proxy_host,
            int(proxy_port),
            dc_id,
            loggers=loggers,
            proxy=None,
            local_addr=local_addr,
            secret=proxy_secret,
            **kwargs,
        )


if MT_PROXY_HOST and MT_PROXY_PORT and MT_PROXY_SECRET:
    client_kwargs = {
        "connection": _FakeTlsProxyConnection,
        "proxy": (MT_PROXY_HOST, MT_PROXY_PORT, MT_PROXY_SECRET),
    }
    print("[TELEGRAM] MTProto FakeTLS proxy configured", flush=True)
else:
    client_kwargs = {
        "connection": TgNetConnection,
    }
    print("[TELEGRAM] MTProto proxy not configured", flush=True)

client = TelegramClient(SESSION_PATH, API_ID, API_HASH, **client_kwargs)
backend = BackendClient(BACKEND_URL, TELEGRAM_BOT_SHARED_SECRET)


class _TextEventAdapter:
    """Expose recognized voice text through the existing message-handler interface."""

    def __init__(self, event: events.NewMessage.Event, text: str) -> None:
        self._event = event
        self.sender_id = event.sender_id
        self.raw_text = text

    async def respond(self, *args, **kwargs):
        return await self._event.respond(*args, **kwargs)


async def _handle_text_event(event: events.NewMessage.Event, text: str) -> None:
    adapted_event = _TextEventAdapter(event, text)
    await handle_device_registration_message(adapted_event, backend, registration_sessions)
    await handle_family_rename_message(adapted_event, backend)
    await handle_registration_message(adapted_event, backend)


@client.on(events.NewMessage)
async def voice_message_handler(event: events.NewMessage.Event) -> None:
    if not event.message.voice:
        return

    with tempfile.TemporaryDirectory() as temp_dir:
        audio_path = Path(temp_dir) / "voice.ogg"
        await event.message.download_media(file=str(audio_path))
        text = await asyncio.to_thread(transcribe_audio, str(audio_path))

    if not text.strip():
        await event.respond("Не удалось распознать голосовое сообщение.")
        return

    await _handle_text_event(event, text)


@client.on(events.NewMessage)
async def registration_message_handler(event: events.NewMessage.Event) -> None:
    if event.message.voice:
        return
    await handle_device_registration_message(event, backend, registration_sessions)
    await handle_family_rename_message(event, backend)
    await handle_registration_message(event, backend)


@client.on(events.CallbackQuery)
async def callback_handler(event: events.CallbackQuery.Event) -> None:
    data = event.data.decode("utf-8") if event.data else ""
    if data.startswith("device_registration:"):
        await handle_device_registration_action(event, backend, registration_sessions)
        return
    if data.startswith("agent_installation:"):
        await handle_agent_installation_action(event, backend)
        return
    if data.startswith("child:"):
        await handle_child_action(event, backend)
        return
    if data.startswith("parent:"):
        await handle_parent_action_base(event, backend)
        return
    if data.startswith("role:"):
        await handle_role(event, backend)
        return


@client.on(events.NewMessage(pattern=r"^/start(?:\s|$)"))
async def start_handler(event: events.NewMessage.Event) -> None:
    await handle_start(event, backend)


async def main() -> None:
    print("[START] Family Beacon Telegram bot", flush=True)
    print("[WHISPER] Loading model: turbo...", flush=True)
    await asyncio.to_thread(load_model)
    print("[WHISPER] Model loaded", flush=True)
    print("[TELEGRAM] Connecting...", flush=True)
    await client.start(bot_token=BOT_TOKEN)
    print("[TELEGRAM] Connected", flush=True)
    print("[BOT] Family Beacon Telegram bot started", flush=True)
    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
