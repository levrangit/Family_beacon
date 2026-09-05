from __future__ import annotations

from datetime import datetime

from telethon import Button, events
from telethon.errors import MessageNotModifiedError

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
    "👋 Добро пожаловать в 🌟 Семейный маяк!\n\n"
    "Выберите свою роль, чтобы продолжить:"
)
ROLE_BUTTONS = [
    [Button.inline("👨 Родитель", b"role:parent")],
    [Button.inline("👦 Ребёнок", b"role:child")],
]
PARENT_MENU_TEXT = "🌟 Семейный маяк"
PARENT_MENU_BUTTONS = [
    [Button.inline("🏠 Семья", b"parent:family")],
    [Button.inline("👤 Профиль", b"parent:profile")],
    [Button.inline("👶 Дети", b"parent:children")],
    [Button.inline("📨 Приглашения", b"parent:invites")],
    [Button.inline("🗑 Забыть меня", b"parent:forget")],
]
BACK_BUTTON = [[Button.inline("◀️ Назад", b"parent:menu")]]
FAMILY_RENAME_BUTTONS = [[Button.inline("◀️ Отмена", b"parent:family:rename:cancel")]]
INVITES_BUTTONS = [
    [Button.inline("➕ Выдать приглашение", b"parent:create_invite")],
    [Button.inline("◀️ Назад", b"parent:menu")],
]
FORGET_CONFIRM_BUTTONS = [
    [Button.inline("❌ Отмена", b"parent:forget:cancel")],
    [Button.inline("🗑 Да, удалить всё", b"parent:forget:confirm")],
]
PARENT_LOGIN_TEXT = "👨 Регистрация родителя\n\nВведите логин (e-mail):"
PARENT_PASSWORD_TEXT = "🔐 Введите пароль:\n\nПароль не будет сохранён в Telegram-боте."
PARENT_WEAK_PASSWORD_TEXT = (
    "🔐 Пароль не прошёл проверку.\n\n"
    "Похоже, пароль слишком простой. Придумайте более сложный пароль — "
    "не менее 8 символов, с буквами и цифрами.\n\n"
    "Попробуйте ввести новый пароль."
)
PARENT_SUCCESS_TEXT = "✅ Регистрация завершена!\n\nВы зарегистрированы как родитель."
PARENT_ERROR_TEXT = "❌ Не удалось завершить регистрацию.\n\nПроверьте данные и попробуйте снова с командой /start."
CHILD_INVITE_TEXT = "👦 Регистрация ребёнка\n\nВведите код приглашения, который выдал родитель."
CHILD_NAME_TEXT = "Введите имя ребёнка:"
CHILD_SUCCESS_TEXT = "✅ Регистрация завершена!"
CHILD_ERROR_TEXT = (
    "❌ Не удалось завершить регистрацию ребёнка.\n\n"
    "Код может быть неверным, просроченным, отозванным или уже использованным. "
    "Также Telegram-аккаунт не может быть зарегистрирован повторно.\n\n"
    "Попробуйте снова с командой /start."
)
ADMIN_MENU_TEXT = "🛡 С возвращением в 🌟 Семейный маяк!\n\nВы зарегистрированы как администратор."
FORGET_CONFIRM_TEXT = (
    "⚠️ Вы действительно хотите забыть себя?\n\n"
    "Будут удалены:\n"
    "• ваш профиль\n"
    "• семья\n"
    "• дети\n"
    "• устройства\n"
    "• приглашения\n\n"
    "Это действие необратимо."
)
FORGET_SUCCESS_TEXT = "✅ Все данные вашего аккаунта удалены.\n\nЕсли захотите зарегистрироваться снова, отправьте /start."
FAMILY_RENAME_TEXT = "✏️ Переименование семьи\n\nВведите новое название семьи:"
FAMILY_RENAME_ERROR_TEXT = "❌ Не удалось изменить название семьи.\n\nПопробуйте ввести другое название."
registration_sessions: dict[int, RegistrationSession] = {}
family_rename_sessions: set[int] = set()


def _parent_family_buttons(family: dict) -> list[list[Button]]:
    buttons: list[list[Button]] = [
        [Button.inline(f"🏠 {family.get('name') or 'Моя семья'}", b"parent:family:rename")]
    ]
    children = family.get("children") or []
    for child in children:
        name = child.get("name") or "Без имени"
        child_id = str(child.get("id"))
        buttons.append([Button.inline(f"👶 {name}", f"parent:family:child:{child_id}".encode())])
    buttons.append([Button.inline("➕ Выдать приглашение", b"parent:create_invite")])
    buttons.append([Button.inline("◀️ Назад", b"parent:menu")])
    return buttons


async def _show_parent_family(event: events.CallbackQuery.Event, backend: BackendClient, *, edit: bool = True) -> None:
    telegram_id = event.sender_id
    if telegram_id is None:
        return
    family = await backend.get_parent_family(telegram_id)
    children = family.get("children") or []
    text = "🏠 Семья" if children else "🏠 Семья\n\nДети не зарегистрированы."
    if edit:
        await event.edit(text, buttons=_parent_family_buttons(family))


async def handle_start(event: events.NewMessage.Event, backend: BackendClient) -> None:
    telegram_id = event.sender_id
    if telegram_id is None:
        return
    registration_sessions.pop(telegram_id, None)
    family_rename_sessions.discard(telegram_id)
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
            await event.respond(format_child_menu(identity), buttons=CHILD_MENU_BUTTONS)
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


async def handle_parent_action(event: events.CallbackQuery.Event, backend: BackendClient) -> None:
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
            await _show_parent_family(event, backend)
        except Exception:
            await event.edit("❌ Не удалось загрузить информацию о семье.", buttons=BACK_BUTTON)
        return
    if data == b"parent:family:rename":
        family_rename_sessions.add(telegram_id)
        try:
            family = await backend.get_parent_family(telegram_id)
            current_name = family.get("name") or "Моя семья"
            await event.edit(
                f"✏️ Переименование семьи\n\nТекущее название:\n{current_name}\n\nВведите новое название семьи:",
                buttons=FAMILY_RENAME_BUTTONS,
            )
        except Exception:
            family_rename_sessions.discard(telegram_id)
            await event.edit("❌ Не удалось загрузить информацию о семье.", buttons=BACK_BUTTON)
        return
    if data == b"parent:family:rename:cancel":
        family_rename_sessions.discard(telegram_id)
        try:
            await _show_parent_family(event, backend)
        except Exception:
            await event.edit("❌ Не удалось загрузить информацию о семье.", buttons=BACK_BUTTON)
        return
    if data.startswith(b"parent:family:child:"):
        child_id = data.decode().split(":", 3)[3]
        try:
            dashboard = await backend.get_parent_child_dashboard(telegram_id, child_id)
        except Exception:
            await event.edit("❌ Не удалось загрузить данные ребёнка.", buttons=BACK_BUTTON)
            return
        child = dashboard.get("child") or {}
        name = child.get("name") or "Без имени"
        buttons = [
            [Button.inline("👤 Мой профиль", f"parent:child:{child_id}:profile".encode())],
            [Button.inline("⏱ Моё время", f"parent:child:{child_id}:time".encode())],
            [Button.inline("💻 Мои устройства", f"parent:child:{child_id}:devices".encode())],
            [Button.inline("◀️ Назад", b"parent:family")],
        ]
        await event.edit(f"👶 {name}", buttons=buttons)
        return
    if data.startswith(b"parent:child:"):
        parts = data.decode().split(":")
        if len(parts) != 4:
            return
        child_id, section = parts[2], parts[3]
        try:
            dashboard = await backend.get_parent_child_dashboard(telegram_id, child_id)
        except Exception:
            await event.edit("❌ Не удалось загрузить данные ребёнка.", buttons=BACK_BUTTON)
            return
        child = dashboard.get("child") or {}
        name = child.get("name") or "Без имени"
        child_menu_button = Button.inline("◀️ Назад", f"parent:family:child:{child_id}".encode())
        if section == "profile":
            text = format_child_profile(child).replace("👤 Мой профиль", f"👤 {name} — профиль")
        elif section == "time":
            text = format_child_time(dashboard).replace("⏱ Моё время", f"⏱ {name} — время")
        elif section == "devices":
            text = format_child_devices(dashboard).replace("💻 Мои устройства", f"💻 {name} — устройства")
        else:
            return
        await event.edit(text, buttons=[[child_menu_button]])
        return
    if data == b"parent:profile":
        try:
            profile = await backend.get_parent_profile(telegram_id)
        except Exception:
            await event.edit("❌ Не удалось загрузить профиль.", buttons=BACK_BUTTON)
            return
        email = profile.get("email") or "—"
        status = "активен" if profile.get("is_active") else "неактивен"
        text = "👤 Профиль\n\n" f"Логин: {email}\n" f"Роль: {profile.get('role', '—')}\n" f"Статус: {status}"
        await event.edit(text, buttons=BACK_BUTTON)
        return
    if data == b"parent:children":
        try:
            children = await backend.get_parent_children(telegram_id)
        except Exception:
            await event.edit("❌ Не удалось загрузить список детей.", buttons=BACK_BUTTON)
            return
        if not children:
            await event.edit("👶 Дети\n\nДети не зарегистрированы.", buttons=BACK_BUTTON)
            return
        buttons = [
            [Button.inline(f"👶 {child.get('name') or 'Без имени'}", f"parent:family:child:{child.get('id')}".encode())]
            for child in children
        ]
        buttons.append([Button.inline("◀️ Назад", b"parent:menu")])
        await event.edit("👶 Дети", buttons=buttons)
        return
    if data == b"parent:invites":
        try:
            invites = await backend.list_parent_invites(telegram_id)
        except Exception:
            await event.edit("❌ Не удалось загрузить приглашения.", buttons=BACK_BUTTON)
            return
        if not invites:
            await event.edit("📨 Приглашения\n\nПриглашений пока нет.", buttons=INVITES_BUTTONS)
            return
        status_labels = {"active": "🟢 Активен", "used": "⚪ Использован", "expired": "🔴 Истёк", "revoked": "🚫 Отозван"}
        lines = ["📨 Приглашения", ""]
        for index, invite in enumerate(invites, start=1):
            code = invite.get("code") or "—"
            expires_at = str(invite.get("expires_at", "—"))
            try:
                expires_at = datetime.fromisoformat(expires_at.replace("Z", "+00:00")).strftime("%d.%m.%Y")
            except ValueError:
                pass
            status = status_labels.get(invite.get("status"), "❓ Неизвестен")
            lines.extend([f"{index}. {status}", f"   Код: {code}", f"   Действует до: {expires_at}", ""])
        await event.edit("\n".join(lines).rstrip(), buttons=INVITES_BUTTONS)
        return
    if data == b"parent:create_invite":
        try:
            invite = await backend.create_parent_invite(telegram_id)
        except Exception:
            await event.edit("❌ Не удалось создать приглашение.", buttons=INVITES_BUTTONS)
            return
        expires_at = str(invite.get("expires_at", "—"))
        try:
            expires_at = datetime.fromisoformat(expires_at.replace("Z", "+00:00")).strftime("%d.%m.%Y")
        except ValueError:
            pass
        text = "🎟 Приглашение создано!\n\n" f"Код: {invite.get('code', '—')}\n\n" f"Действительно до: {expires_at}\n\n" "Передайте этот код ребёнку."
        await event.edit(text, buttons=INVITES_BUTTONS)
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
            await event.edit("❌ Не удалось удалить аккаунт. Данные не были подтверждены как удалённые.\n\nПопробуйте ещё раз позже.", buttons=BACK_BUTTON)
            return
        await event.edit(FORGET_SUCCESS_TEXT)


async def handle_child_action(event: events.CallbackQuery.Event, backend: BackendClient) -> None:
    await event.answer()
    telegram_id = event.sender_id
    if telegram_id is None:
        return
    data = event.data or b""
    if data == b"child:menu":
        try:
            dashboard = await backend.get_child_dashboard(telegram_id)
        except Exception:
            try:
                await event.edit("❌ Не удалось загрузить меню ребёнка.", buttons=CHILD_BACK_BUTTON)
            except MessageNotModifiedError:
                pass
            return
        await event.edit(format_child_menu(dashboard["child"]), buttons=CHILD_MENU_BUTTONS)
        return
    try:
        dashboard = await backend.get_child_dashboard(telegram_id)
    except Exception:
        try:
            await event.edit("❌ Не удалось загрузить данные ребёнка.", buttons=CHILD_BACK_BUTTON)
        except MessageNotModifiedError:
            pass
        return
    if data == b"child:profile":
        await event.edit(format_child_profile(dashboard["child"]), buttons=CHILD_BACK_BUTTON)
        return
    if data == b"child:time":
        await event.edit(format_child_time(dashboard), buttons=CHILD_BACK_BUTTON)
        return
    if data == b"child:devices":
        await event.edit(format_child_devices(dashboard), buttons=CHILD_BACK_BUTTON)
        return


async def handle_registration_message(event: events.NewMessage.Event, backend: BackendClient) -> None:
    """Process text entered during parent or child registration."""
    telegram_id = event.sender_id
    if telegram_id is None:
        return
    text = (event.raw_text or "").strip()
    if not text:
        return
    if telegram_id in family_rename_sessions:
        try:
            family = await backend.rename_parent_family(telegram_id, text)
        except Exception:
            await event.respond(FAMILY_RENAME_ERROR_TEXT)
            return
        family_rename_sessions.discard(telegram_id)
        await event.respond(f"✅ Название семьи изменено.\n\nНовое название:\n{family.get('name') or text}")
        try:
            family = await backend.get_parent_family(telegram_id)
            await event.respond("", buttons=_parent_family_buttons(family))
        except Exception:
            pass
        return
    session = registration_sessions.get(telegram_id)
    if session is None:
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
            except ValueError as exc:
                if str(exc) == "Password is too weak":
                    await event.respond(PARENT_WEAK_PASSWORD_TEXT)
                else:
                    await event.respond(f"❌ {exc}\n\n{PARENT_PASSWORD_TEXT}")
                return
            try:
                await backend.register_parent(**registration_data)
            except Exception:
                await event.respond(PARENT_ERROR_TEXT)
                return
            registration_sessions.pop(telegram_id, None)
            await event.respond(PARENT_SUCCESS_TEXT)
            await event.respond(PARENT_MENU_TEXT, buttons=PARENT_MENU_BUTTONS)
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
            await event.respond(CHILD_MENU_TEXT, buttons=CHILD_MENU_BUTTONS)
