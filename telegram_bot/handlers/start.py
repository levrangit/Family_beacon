from __future__ import annotations

from typing import Any

from telethon import Button, events

from telegram_bot.backend_client import BackendClient
from telegram_bot.registration import RegistrationSession

WELCOME_TEXT = (
    "👋 Добро пожаловать в Family Beacon!\n\n"
    "Выберите свою роль, чтобы продолжить:"
)

ROLE_BUTTONS = [
    [Button.inline("👨 Родитель", b"role:parent")],
    [Button.inline("👦 Ребёнок", b"role:child")],
]

PARENT_LOGIN_TEXT = (
    "👨 Регистрация родителя\n\n"
    "Введите логин (e-mail):"
)

PARENT_PASSWORD_TEXT = (
    "🔐 Введите пароль:\n\n"
    "Пароль не будет сохранён в Telegram-боте."
)

PARENT_SUCCESS_TEXT = (
    "✅ Регистрация завершена!\n\n"
    "Вы зарегистрированы как родитель."
)

PARENT_ERROR_TEXT = (
    "❌ Не удалось завершить регистрацию.\n\n"
    "Проверьте данные и попробуйте снова с командой /start."
)

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


registration_sessions: dict[int, RegistrationSession] = {}


async def handle_start(event: events.NewMessage.Event, backend: BackendClient) -> None:
    """Handle /start using the Telegram ID lookup flow."""
    telegram_id = event.sender_id
    if telegram_id is None:
        return

    registration_sessions.pop(telegram_id, None)

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
    telegram_id = event.sender_id
    if telegram_id is None:
        return

    if data == b"role:parent":
        session = RegistrationSession(telegram_id=telegram_id)
        session.start_parent_registration()
        registration_sessions[telegram_id] = session
        await event.edit(PARENT_LOGIN_TEXT)
    elif data == b"role:child":
        await event.edit("👦 Вы выбрали роль «Ребёнок».\n\nСледующий шаг — регистрация.")


async def handle_registration_message(
    event: events.NewMessage.Event,
    backend: BackendClient,
) -> None:
    """Process text entered during parent registration."""
    telegram_id = event.sender_id
    if telegram_id is None:
        return

    session = registration_sessions.get(telegram_id)
    if session is None or session.role != "parent":
        return

    text = (event.raw_text or "").strip()
    if not text:
        return

    if session.state == "waiting_login":
        try:
            session.set_login(text)
        except ValueError as exc:
            await event.respond(f"❌ {exc}\n\n{PARENT_LOGIN_TEXT}")
            return

        await event.respond(PARENT_PASSWORD_TEXT)
        return

    if session.state == "waiting_password":
        try:
            registration_data = session.complete_parent_registration(text)
            await backend.register_parent(**registration_data)
        except (ValueError, Exception):
            await event.respond(PARENT_ERROR_TEXT)
            return

        registration_sessions.pop(telegram_id, None)
        await event.respond(PARENT_SUCCESS_TEXT)
