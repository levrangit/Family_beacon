from __future__ import annotations

from datetime import datetime

from telethon import Button, events

from telegram_bot.backend_client import BackendClient


AGENT_INSTALLATION_BUTTONS = [
    [Button.inline("◀️ Назад", b"parent:family")],
]


def parent_family_buttons_with_installation(family: dict) -> list[list[Button]]:
    buttons: list[list[Button]] = [
        [Button.inline(f"🏠 {family.get('name') or 'Семья'}", b"parent:family:rename")]
    ]
    children = family.get("children") or []
    for child in children:
        name = child.get("name") or "Без имени"
        child_id = str(child.get("id"))
        buttons.append(
            [Button.inline(f"👶 {name}", f"parent:family:child:{child_id}".encode())]
        )
    buttons.append([Button.inline("➕ Выдать приглашение", b"parent:create_invite")])
    buttons.append([Button.inline("👤 Профиль", b"parent:profile")])
    buttons.append([Button.inline("💻 Создать установку Agent", b"parent:agent_installation")])
    buttons.append([Button.inline("◀️ Назад", b"parent:menu")])
    return buttons


def format_agent_installation(installation: dict) -> str:
    expires_at = str(installation.get("expires_at", "—"))
    try:
        expires_at = datetime.fromisoformat(
            expires_at.replace("Z", "+00:00")
        ).strftime("%d.%m.%Y %H:%M UTC")
    except ValueError:
        pass

    return (
        "💻 Установка Family Beacon Agent\n\n"
        f"Код установки: {installation.get('installation_code', '—')}\n\n"
        f"Действует до: {expires_at}\n\n"
        "Передайте этот код человеку, который устанавливает официальный "
        "Family Beacon Agent на компьютер. Код можно использовать только один раз."
    )


async def handle_agent_installation_action(
    event: events.CallbackQuery.Event,
    backend: BackendClient,
) -> None:
    await event.answer()
    telegram_id = event.sender_id
    if telegram_id is None:
        return

    data = event.data or b""
    if data != b"parent:agent_installation":
        return

    try:
        installation = await backend.create_agent_installation(telegram_id)
    except Exception:
        await event.edit(
            "❌ Не удалось создать установку Agent.\n\nПопробуйте ещё раз.",
            buttons=AGENT_INSTALLATION_BUTTONS,
        )
        return

    await event.edit(
        format_agent_installation(installation),
        buttons=AGENT_INSTALLATION_BUTTONS,
    )
