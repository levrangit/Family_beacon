"""Telegram-facing device registration helpers."""

from __future__ import annotations

DEVICE_REGISTRATION_STATUSES = {
    "accepted": "✅ Код принят.\n\nРегистрация ожидает подтверждения родителя.",
    "waiting_parent_approval": "⏳ Регистрация ожидает подтверждения родителя.",
    "approved": "✅ Регистрация устройства одобрена родителем.",
    "rejected": "❌ Регистрация устройства отклонена родителем.",
    "timeout": "⌛ Регистрация завершилась: родитель не подтвердил её в течение 10 минут.",
    "invalid": "❌ Код регистрации неверен.",
    "expired": "⌛ Код регистрации просрочен.",
    "already_used": "❌ Этот код регистрации уже использован.",
}


def registration_code_prompt() -> str:
    """Return the child-facing prompt for a device registration code."""
    return (
        "💻 Регистрация устройства\n\n"
        "Введите временный код, который показан в приложении Family Beacon "
        "на компьютере ребёнка.\n\n"
        "Код действует ограниченное время и предназначен только для этой регистрации."
    )


def registration_result(status: str) -> str:
    """Return user-facing text for a device registration status."""
    return DEVICE_REGISTRATION_STATUSES.get(
        status,
        "⚠️ Не удалось определить состояние регистрации устройства.",
    )
