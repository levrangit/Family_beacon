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

PARENT_MENU_TEXT = (
    "👨 С возвращением в Family Beacon!\n\n"
    "Вы зарегистрированы как родитель."
)

ADMIN_MENU_TEXT = (
    "🛡 С возвращением в Family Beacon!\n\n"
    "Вы зарегистрированы как администратор."
)

CHILD_MENU_TEXT = (
    "👦 С возвращением в Family Beacon!\n\n"
    "Вы зарегистрированы как ребёнок."
)


async def handle_start(event: events.NewMessage.Event, backend: BackendClient) -> None:
    """Handle /start using the Telegram ID lookup flow."""
    telegram_id = event.sender_id
    if telegram_id is None:
        return

    identity = await backend.lookup_telegram_id(telegram_id)

    if identity is not None:
        identity_type = identity.get("type")

        if identity_type == "profile":
            role = identity.get("role")
            if role == "parent":
                await event.respond(PARENT_MENU_TEXT)
                return
            if role == "admin":
                await event.respond(ADMIN_MENU_TEXT)
                return

        if identity_type == "child":
            await event.respond(CHILD_MENU_TEXT)
            return

    await event.respond(WELCOME_TEXT, buttons=ROLE_BUTTONS)


async def handle_role(event: events.CallbackQuery.Event) -> None:
    await event.answer()

    data = event.data or b""
    if data == b"role:parent":
        await event.edit("👨 Вы выбрали роль «Родитель».\n\nСледующий шаг — регистрация.")
    elif data == b"role:child":
        await event.edit("👦 Вы выбрали роль «Ребёнок».\n\nСледующий шаг — регистрация.")
