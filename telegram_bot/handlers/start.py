from __future__ import annotations

from datetime import datetime

from telethon import Button, events

from telegram_bot.backend_client import BackendClient
from telegram_bot.child_menu import (
    CHILD_BACK_BUTTON,
    CHILD_MENU_BUTTONS,
    CHILD_MENU_TEXT,
    format_child_devices,
    format_child_menu,
    format_child_profile,
    format_child_time,
)
from telegram_bot.registration import RegistrationSession

WELCOME_TEXT = (
    "👋 Добро пожаловать в Family Beacon!\n\n"
    "Выберите свою роль, чтобы продолжить:"
)

ROLE_BUTTONS = [
    [Button.inline("👨 Родитель", b"role:parent")],
    [Button.inline("👦 Ребёнок", b"role:child")],
]

PARENT_MENU_TEXT = "👨 Family Beacon\n\nВыберите действие:"
PARENT_MENU_BUTTONS = [
    [Button.inline("🏠 Моя семья", b"parent:family")],
    [Button.inline("👤 Мой профиль", b"parent:profile")],
    [Button.inline("👶 Дети", b"parent:children")],
    [Button.inline("📨 Мои приглашения", b"parent:invites")],
    [Button.inline("➕ Выдать приглашение ребенку", b"parent:create_invite")],
    [Button.inline("🗑 Забыть меня", b"parent:forget")],
]

BACK_BUTTON = [[Button.inline("◀️ Назад", b"parent:menu")]]
FORGET_CONFIRM_BUTTONS = [
    [Button.inline("❌ Отмена", b"parent:forget:cancel")],
    [Button.inline("🗑 Да, удалить всё", b"parent:forget:confirm")],
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

CHILD_INVITE_TEXT = (
    "👦 Регистрация ребёнка\n\n"
    "Введите код приглашения, который выдал родитель."
)

CHILD_NAME_TEXT = "Введите имя ребёнка:"

CHILD_SUCCESS_TEXT = (
    "✅ Регистрация завершена!\n\n"
    "Вы зарегистрированы как ребёнок."
)

CHILD_ERROR_TEXT = (
    "❌ Не удалось завершить регистрацию ребёнка.\n\n"
    "Код может быть неверным, просроченным, отозванным или уже использованным. "
    "Также Telegram-аккаунт не может быть зарегистрирован повторно.\n\n"
    "Попробуйте снова с командой /start."
)

ADMIN_MENU_TEXT = (
    "🛡 С возвращением в Family Beacon!\n\n"
    "Вы зарегистрированы как администратор."
)

FORGET_CONFIRM_TEXT = (
    "⚠️ Вы действительно хотите забыть себя?\n\n"
    "Будут удалены:\n"
    "• ваш профиль\n"
    "• семья\n"
    "• дети\n"
    "• устройства\n"
    "• приглашения\n"
    "• связанные данные\n\n"
    "Это действие необратимо."
)

FORGET_SUCCESS_TEXT = (
    "✅ Все данные вашего аккаунта удалены.\n\n"
    "Если захотите зарегистрироваться снова, отправьте /start."
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
                await event.respond(PARENT_MENU_TEXT, buttons=PARENT_MENU_BUTTONS)
                return
            if role == "admin":
                await event.respond(ADMIN_MENU_TEXT)
                return

        if identity_type == "child":
            await event.respond(
                format_child_menu(identity),
                buttons=CHILD_MENU_BUTTONS,
            )
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
        session = RegistrationSession(telegram_id=telegram_id)
        session.start_child_registration()
        registration_sessions[telegram_id] = session
        await event.edit(CHILD_INVITE_TEXT)


async def handle_parent_action(
    event: events.CallbackQuery.Event,
    backend: BackendClient,
) -> None:
    await event.answer()

    telegram_id = event.sender_id
    if telegram_id is None:
        return

    data = event.data or b""

    if data == b"parent:menu":
        await event.edit(PARENT_MENU_TEXT, buttons=PARENT_MENU_BUTTONS)
        return

    if data == b"parent:family":
        try:
            family = await backend.get_parent_family(telegram_id)
        except Exception:
            await event.edit("❌ Не удалось загрузить информацию о семье.", buttons=BACK_BUTTON)
            return

        children = family.get("children") or []
        text = (
            "🏠 Моя семья\n\n"
            f"Название: {family.get('name', '—')}\n"
            f"Детей: {len(children)}"
        )
        await event.edit(text, buttons=BACK_BUTTON)
        return

    if data == b"parent:profile":
        try:
            profile = await backend.get_parent_profile(telegram_id)
        except Exception:
            await event.edit("❌ Не удалось загрузить профиль.", buttons=BACK_BUTTON)
            return

        email = profile.get("email") or "—"
        status = "активен" if profile.get("is_active") else "неактивен"
        text = (
            "👤 Мой профиль\n\n"
            f"Логин: {email}\n"
            f"Telegram ID: {profile.get('telegram_id', '—')}\n"
            f"Роль: {profile.get('role', '—')}\n"
            f"Статус: {status}"
        )
        await event.edit(text, buttons=BACK_BUTTON)
        return

    if data == b"parent:children":
        try:
            children = await backend.get_parent_children(telegram_id)
        except Exception:
            await event.edit("❌ Не удалось загрузить список детей.", buttons=BACK_BUTTON)
            return

        if not children:
            await event.edit("👶 Дети\n\nДетей пока нет.", buttons=BACK_BUTTON)
            return

        lines = ["👶 Дети", ""]
        for child in children:
            status = "активен" if child.get("is_active") else "неактивен"
            lines.append(f"• {child.get('name', '—')} — {status}")

        await event.edit("\n".join(lines), buttons=BACK_BUTTON)
        return

    if data == b"parent:invites":
        try:
            invites = await backend.list_parent_invites(telegram_id)
        except Exception:
            await event.edit("❌ Не удалось загрузить приглашения.", buttons=BACK_BUTTON)
            return

        if not invites:
            await event.edit("📨 Мои приглашения\n\nПриглашений пока нет.", buttons=BACK_BUTTON)
            return

        status_labels = {
            "active": "🟢 Активен",
            "used": "⚪ Использован",
            "expired": "🔴 Истёк",
            "revoked": "🚫 Отозван",
        }
        lines = ["📨 Мои приглашения", ""]
        for index, invite in enumerate(invites, start=1):
            code = invite.get("code") or "—"
            expires_at = str(invite.get("expires_at", "—"))
            try:
                expires_at = datetime.fromisoformat(
                    expires_at.replace("Z", "+00:00")
                ).strftime("%d.%m.%Y")
            except ValueError:
                pass

            status = status_labels.get(invite.get("status"), "❓ Неизвестен")
            lines.extend(
                [
                    f"{index}. {status}",
                    f"   Код: {code}",
                    f"   Действует до: {expires_at}",
                    "",
                ]
            )

        await event.edit("\n".join(lines).rstrip(), buttons=BACK_BUTTON)
        return

    if data == b"parent:create_invite":
        try:
            invite = await backend.create_parent_invite(telegram_id)
        except Exception:
            await event.edit("❌ Не удалось создать приглашение.", buttons=BACK_BUTTON)
            return

        expires_at = str(invite.get("expires_at", "—"))
        try:
            expires_at = datetime.fromisoformat(
                expires_at.replace("Z", "+00:00")
            ).strftime("%d.%m.%Y")
        except ValueError:
            pass

        text = (
            "🎟 Приглашение создано!\n\n"
            f"Код: {invite.get('code', '—')}\n\n"
            f"Действительно до: {expires_at}\n\n"
            "Передайте этот код ребёнку."
        )
        await event.edit(text, buttons=BACK_BUTTON)
        return

    if data == b"parent:forget":
        await event.edit(FORGET_CONFIRM_TEXT, buttons=FORGET_CONFIRM_BUTTONS)
        return

    if data == b"parent:forget:cancel":
        await event.edit(PARENT_MENU_TEXT, buttons=PARENT_MENU_BUTTONS)
        return

    if data == b"parent:forget:confirm":
        try:
            await backend.delete_parent_account(telegram_id)
        except Exception:
            await event.edit(
                "❌ Не удалось удалить аккаунт. Данные не были подтверждены как удалённые.\n\n"
                "Попробуйте ещё раз позже.",
                buttons=BACK_BUTTON,
            )
            return

        await event.edit(FORGET_SUCCESS_TEXT)


async def handle_child_action(
    event: events.CallbackQuery.Event,
    backend: BackendClient,
) -> None:
    await event.answer()

    telegram_id = event.sender_id
    if telegram_id is None:
        return

    data = event.data or b""

    if data == b"child:menu":
        try:
            dashboard = await backend.get_child_dashboard(telegram_id)
        except Exception:
            await event.edit(
                "❌ Не удалось загрузить меню ребёнка.",
                buttons=CHILD_BACK_BUTTON,
            )
            return

        await event.edit(
            format_child_menu(dashboard["child"]),
            buttons=CHILD_MENU_BUTTONS,
        )
        return

    try:
        dashboard = await backend.get_child_dashboard(telegram_id)
    except Exception:
        await event.edit(
            "❌ Не удалось загрузить данные ребёнка.",
            buttons=CHILD_BACK_BUTTON,
        )
        return

    if data == b"child:profile":
        await event.edit(
            format_child_profile(dashboard["child"]),
            buttons=CHILD_BACK_BUTTON,
        )
        return

    if data == b"child:time":
        await event.edit(
            format_child_time(dashboard),
            buttons=CHILD_BACK_BUTTON,
        )
        return

    if data == b"child:devices":
        await event.edit(
            format_child_devices(dashboard),
            buttons=CHILD_BACK_BUTTON,
        )
        return


async def handle_registration_message(
    event: events.NewMessage.Event,
    backend: BackendClient,
) -> None:
    """Process text entered during parent or child registration."""
    telegram_id = event.sender_id
    if telegram_id is None:
        return

    session = registration_sessions.get(telegram_id)
    if session is None:
        return

    text = (event.raw_text or "").strip()
    if not text:
        return

    if session.role == "parent":
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
            except Exception:
                await event.respond(PARENT_ERROR_TEXT)
                return

            registration_sessions.pop(telegram_id, None)
            await event.respond(PARENT_SUCCESS_TEXT)
            return

    if session.role == "child":
        if session.state == "waiting_invite_code":
            try:
                session.set_invite_code(text)
            except ValueError as exc:
                await event.respond(f"❌ {exc}\n\n{CHILD_INVITE_TEXT}")
                return

            await event.respond(CHILD_NAME_TEXT)
            return

        if session.state == "waiting_child_name":
            try:
                registration_data = session.complete_child_registration(text)
                await backend.register_child(**registration_data)
            except Exception:
                await event.respond(CHILD_ERROR_TEXT)
                return

            registration_sessions.pop(telegram_id, None)
            await event.respond(CHILD_SUCCESS_TEXT)
