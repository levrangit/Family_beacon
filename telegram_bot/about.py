from __future__ import annotations

from telethon import Button, events

from telegram_bot.config import AUTHOR_TELEGRAM_ID

ABOUT_TEXT = (
    "🌟 Семейный маяк\n\n"
    "Семейный маяк помогает родителям заботиться о цифровой безопасности детей.\n\n"
    "С помощью программы родитель может управлять временем использования устройств, "
    "видеть подключённые устройства и получать информацию о состоянии детского устройства.\n\n"
    "Программа находится в разработке.\n\n"
    "Спасибо, что пользуетесь Семейным маяком! ❤️"
)
ABOUT_BUTTONS = [
    [Button.inline("💝 Сказать спасибо автору", b"parent:about:thanks")],
    [Button.inline("◀️ Назад", b"parent:menu")],
]


def _thank_you_text(telegram_id: int, username: str | None) -> str:
    user = f"@{username}" if username else f"Telegram ID {telegram_id}"
    return f'💌 Пользователь {user} сказал вам «Спасибо!»'


async def handle_about_action(event: events.CallbackQuery.Event) -> None:
    await event.answer()
    telegram_id = event.sender_id
    if telegram_id is None:
        return
    data = event.data or b""
    if data == b"parent:about":
        await event.edit(ABOUT_TEXT, buttons=ABOUT_BUTTONS)
        return
    if data == b"parent:about:thanks":
        if not AUTHOR_TELEGRAM_ID:
            await event.edit("❌ Благодарность пока не настроена.", buttons=ABOUT_BUTTONS)
            return
        sender = await event.get_sender()
        username = getattr(sender, "username", None)
        await event.client.send_message(
            AUTHOR_TELEGRAM_ID,
            _thank_you_text(telegram_id, username),
        )
        await event.edit(
            "❤️ Спасибо! Ваше сообщение отправлено автору.",
            buttons=ABOUT_BUTTONS,
        )
