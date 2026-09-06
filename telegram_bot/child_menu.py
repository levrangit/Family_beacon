from __future__ import annotations

from typing import Any

from telethon import Button

from telegram_bot.version import get_project_version


CHILD_MENU_TEXT = f"🌟 Семейный маяк · {get_project_version()}"
CHILD_MENU_BUTTONS = [
    [Button.inline("👤 Профиль", b"child:profile")],
    [Button.inline("⏱ Время", b"child:time")],
    [Button.inline("💻 Устройства", b"child:devices")],
]

CHILD_DEVICES_BUTTONS = [
    [Button.inline("➕ Зарегистрировать устройство", b"child:device_register")],
    [Button.inline("◀️ Назад", b"child:menu")],
]

CHILD_BACK_BUTTON = [[Button.inline("◀️ Назад", b"child:menu")]]


def format_child_menu(child: dict[str, Any]) -> str:
    name = child.get("name") or "—"
    return f"{CHILD_MENU_TEXT}\n\nПривет, {name}!"


def format_child_profile(child: dict[str, Any]) -> str:
    status = "активен" if child.get("is_active") else "неактивен"
    name = child.get("name") or "—"
    return (
        "👤 Профиль\n\n"
        f"Имя: {name}\n"
        f"Статус: {status}"
    )


def format_child_time(dashboard: dict[str, Any]) -> str:
    usage = dashboard.get("today_usage") or {}
    policy = dashboard.get("today_policy")

    used = int(usage.get("used_minutes") or 0)
    lines = ["⏱ Время", "", f"Использовано сегодня: {used} мин."]

    if policy and policy.get("is_enabled", True):
        limit = int(policy.get("daily_limit_minutes") or 0)
        remaining = max(limit - used, 0)
        lines.extend(
            [
                f"Лимит сегодня: {limit} мин.",
                f"Осталось: {remaining} мин.",
            ]
        )
    else:
        lines.append("Лимит сегодня: не установлен")

    return "\n".join(lines)


def format_child_devices(dashboard: dict[str, Any]) -> str:
    devices = dashboard.get("devices") or []
    if not devices:
        return "💻 Устройства\n\nУстройства пока не подключены."

    lines = ["💻 Устройства", ""]
    for device in devices:
        status = "🟢 онлайн" if device.get("is_online") else "⚪ офлайн"
        name = device.get("name") or device.get("hostname") or "Без имени"
        platform = device.get("platform") or "—"
        lines.append(f"• {name} — {status} ({platform})")

    return "\n".join(lines)


def format_child_device_registration() -> str:
    return (
        "💻 Регистрация устройства\n\n"
        "Введите временный код, который показан в приложении Family Beacon "
        "на компьютере ребёнка.\n\n"
        "Код действует ограниченное время и предназначен только для этой регистрации."
    )
