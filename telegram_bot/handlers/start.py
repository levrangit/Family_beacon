from __future__ import annotations

from telethon import Button, events

from telegram_bot.backend_client import BackendClient

WELCOME_TEXT = (
    "👋 Добро пожаловать в Family Beacon!\n\n"
    "Выберите свою роль, чтобы продолжить:"
)

ROLE_BUTTONS = [
    [Button.inline("👨 Родитель", b"role:parent")],
    [Button.inline("👦 Ребёнок", b"role:child")],
]


async def handle_start(event: events.NewMessage.Event, backend: BackendClient) -> None:
    """Temporary registration stub: every /start is treated as a new user."""
    del backend
    await event.respond(WELCOME_TEXT, buttons=ROLE_BUTTONS)


async def handle_role(event: events.CallbackQuery.Event) -> None:
    await event.answer()

    data = event.data or b""
    if data == b"role:parent":
        await event.edit("👨 Вы выбрали роль «Родитель».\n\nСледующий шаг — регистрация.")
    elif data == b"role:child":
        await event.edit("👦 Вы выбрали роль «Ребёнок».\n\nСледующий шаг — регистрация.")
