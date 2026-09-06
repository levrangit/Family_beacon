from __future__ import annotations

from telethon import Button, events

from telegram_bot.backend_client import BackendClient
from telegram_bot.handlers.start import family_rename_sessions


FAMILY_RENAME_SUCCESS_BUTTONS = [[Button.inline("◀️ Назад", b"parent:family")]]


async def handle_family_rename_message(
    event: events.NewMessage.Event,
    backend: BackendClient,
) -> bool:
    telegram_id = event.sender_id
    if telegram_id is None or telegram_id not in family_rename_sessions:
        return False

    text = (event.raw_text or "").strip()
    if not text:
        return True

    try:
        family = await backend.rename_parent_family(telegram_id, text)
    except Exception:
        await event.respond(
            "❌ Не удалось изменить название семьи.\n\n"
            "Попробуйте ввести другое название.",
        )
        return True

    family_rename_sessions.discard(telegram_id)
    new_name = family.get("name") or text
    await event.respond(
        f"✅ Название семьи изменено.\n\nНовое название:\n{new_name}",
        buttons=FAMILY_RENAME_SUCCESS_BUTTONS,
    )
    return True
