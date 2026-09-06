from __future__ import annotations

from typing import Any

from telethon import events

from telegram_bot.backend_client import BackendClient
from telegram_bot.child_menu import (
    CHILD_DEVICE_REGISTRATION_BUTTONS,
    CHILD_DEVICES_BUTTONS,
    format_child_device_registration,
    format_child_devices,
)
from telegram_bot.registration import RegistrationSession


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


def registration_result(status: str) -> str:
    """Return user-facing text for a device registration status."""
    return DEVICE_REGISTRATION_STATUSES.get(
        status,
        "⚠️ Не удалось определить состояние регистрации устройства.",
    )


def _status_from_response(payload: dict[str, Any]) -> str:
    return str(payload.get("status") or "unknown").lower()


async def _show_child_devices(
    event: events.CallbackQuery.Event,
    backend: BackendClient,
    telegram_id: int,
) -> None:
    try:
        dashboard = await backend.get_child_dashboard(telegram_id)
    except Exception:
        await event.edit("❌ Не удалось загрузить устройства.", buttons=CHILD_DEVICES_BUTTONS)
        return

    await event.edit(
        format_child_devices(dashboard),
        buttons=CHILD_DEVICES_BUTTONS,
    )


async def handle_device_registration_action(
    event: events.CallbackQuery.Event,
    backend: BackendClient,
    registration_sessions: dict[int, RegistrationSession],
) -> None:
    telegram_id = event.sender_id
    if telegram_id is None:
        return

    data = event.data or b""
    if data in {b"child:devices_menu", b"child:device_registration_back"}:
        await event.answer()
        if data == b"child:device_registration_back":
            registration_sessions.pop(telegram_id, None)
        await _show_child_devices(event, backend, telegram_id)
        return

    if data != b"child:device_register":
        return

    await event.answer()
    session = RegistrationSession(telegram_id=telegram_id)
    session.start_device_registration()
    registration_sessions[telegram_id] = session
    await event.edit(
        format_child_device_registration(),
        buttons=CHILD_DEVICE_REGISTRATION_BUTTONS,
    )


async def handle_device_registration_message(
    event: events.NewMessage.Event,
    backend: BackendClient,
    registration_sessions: dict[int, RegistrationSession],
) -> bool:
    telegram_id = event.sender_id
    if telegram_id is None:
        return False

    session = registration_sessions.get(telegram_id)
    if session is None or session.state != "waiting_device_registration_code":
        return False

    text = (event.raw_text or "").strip()
    if not text:
        return True

    try:
        session.set_device_registration_code(text)
        payload = session.complete_device_registration_code()
        response = await backend.submit_device_registration_code(**payload)
    except ValueError as exc:
        session.state = "waiting_device_registration_code"
        session.device_registration_code = None
        await event.respond(
            f"❌ {exc}\n\nВведите код ещё раз.",
            buttons=CHILD_DEVICE_REGISTRATION_BUTTONS,
        )
        return True
    except Exception:
        session.state = "waiting_device_registration_code"
        session.device_registration_code = None
        await event.respond(
            "❌ Не удалось проверить код регистрации.\n\n"
            "Попробуйте ещё раз позже.",
            buttons=CHILD_DEVICE_REGISTRATION_BUTTONS,
        )
        return True

    status = _status_from_response(response)
    if status in {"invalid", "expired", "already_used"}:
        session.state = "waiting_device_registration_code"
        session.device_registration_code = None
        await event.respond(
            registration_result(status),
            buttons=CHILD_DEVICE_REGISTRATION_BUTTONS,
        )
        return True

    await event.respond(registration_result(status))
    if status in {"accepted", "waiting_parent_approval", "approved", "rejected", "timeout"}:
        registration_sessions.pop(telegram_id, None)
    return True
