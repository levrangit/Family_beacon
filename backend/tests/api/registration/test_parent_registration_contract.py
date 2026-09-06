import pytest

from app.parent_registration import ParentRegistrationRequest


def test_parent_registration_request_accepts_required_fields():
    request = ParentRegistrationRequest(
        telegram_id=123456789,
        login="parent@example.com",
        password="secret123",
    )

    assert request.telegram_id == 123456789
    assert request.login == "parent@example.com"
    assert request.password == "secret123"


def test_parent_registration_requires_telegram_id():
    with pytest.raises(Exception):
        ParentRegistrationRequest(
            login="parent@example.com",
            password="secret123",
        )


def test_parent_registration_requires_login():
    with pytest.raises(Exception):
        ParentRegistrationRequest(
            telegram_id=123456789,
            password="secret123",
        )


def test_parent_registration_requires_password():
    with pytest.raises(Exception):
        ParentRegistrationRequest(
            telegram_id=123456789,
            login="parent@example.com",
        )


def test_parent_registration_login_must_be_valid_email():
    with pytest.raises(Exception):
        ParentRegistrationRequest(
            telegram_id=123456789,
            login="parent",
            password="secret123",
        )
