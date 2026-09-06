from telegram_bot.device_registration_handlers import registration_result
from telegram_bot.registration import RegistrationSession


def test_device_registration_session_starts_in_code_state():
    session = RegistrationSession(telegram_id=123456789)

    session.start_device_registration()

    assert session.role == "child"
    assert session.state == "waiting_device_registration_code"


def test_device_registration_code_is_normalized():
    session = RegistrationSession(telegram_id=123456789)

    session.start_device_registration()
    session.set_device_registration_code(" abcd-2345 ")

    assert session.device_registration_code == "ABCD-2345"
    assert session.state == "waiting_device_registration_code"


def test_device_registration_code_requires_value():
    session = RegistrationSession(telegram_id=123456789)

    session.start_device_registration()

    try:
        session.set_device_registration_code("   ")
        assert False, "Empty device registration code must be rejected"
    except ValueError as exc:
        assert str(exc) == "Device registration code is required"


def test_device_registration_payload_moves_to_parent_approval():
    session = RegistrationSession(telegram_id=123456789)

    session.start_device_registration()
    session.set_device_registration_code("ABCD-2345")

    result = session.complete_device_registration_code()

    assert session.state == "waiting_parent_approval"
    assert result == {
        "telegram_id": 123456789,
        "registration_code": "ABCD-2345",
    }


def test_device_registration_cannot_complete_without_code():
    session = RegistrationSession(telegram_id=123456789)

    session.start_device_registration()

    try:
        session.complete_device_registration_code()
        assert False, "Device registration must not complete without code"
    except ValueError as exc:
        assert str(exc) == "Device registration code is required"

    assert session.state == "waiting_device_registration_code"


def test_device_registration_status_messages_cover_required_states():
    assert "Код принят" in registration_result("accepted")
    assert "неверен" in registration_result("invalid")
    assert "просрочен" in registration_result("expired")
    assert "ожидает подтверждения родителя" in registration_result("waiting_parent_approval")
    assert "одобрена" in registration_result("approved")
    assert "отклонена" in registration_result("rejected")
    assert "10 минут" in registration_result("timeout")
