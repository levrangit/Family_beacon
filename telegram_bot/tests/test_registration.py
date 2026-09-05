from telegram_bot.registration import RegistrationSession


def test_new_user_can_start_parent_registration():
    session = RegistrationSession(telegram_id=123456789)

    session.start_parent_registration()

    assert session.role == "parent"
    assert session.state == "waiting_login"


def test_new_user_can_start_child_registration():
    session = RegistrationSession(telegram_id=123456789)

    session.start_child_registration()

    assert session.role == "child"
    assert session.state == "waiting_invite_code"


def test_child_registration_accepts_invite_code_and_normalizes_it():
    session = RegistrationSession(telegram_id=123456789)

    session.start_child_registration()
    session.set_invite_code(" abcd-2345 ")

    assert session.invite_code == "ABCD-2345"
    assert session.state == "waiting_child_name"


def test_child_registration_completes_with_name():
    session = RegistrationSession(telegram_id=123456789)

    session.start_child_registration()
    session.set_invite_code("ABCD-2345")

    result = session.complete_child_registration(" Alice ")

    assert session.state == "completed"
    assert result == {
        "telegram_id": 123456789,
        "invite_code": "ABCD-2345",
        "child_name": "Alice",
    }


def test_child_registration_requires_invite_code():
    session = RegistrationSession(telegram_id=123456789)

    session.start_child_registration()

    try:
        session.complete_child_registration("Alice")
        assert False, "Child registration must not complete without invite code"
    except ValueError as exc:
        assert str(exc) == "Invite code is required"

    assert session.state == "waiting_invite_code"


def test_child_registration_rejects_empty_invite_code():
    session = RegistrationSession(telegram_id=123456789)

    session.start_child_registration()

    try:
        session.set_invite_code("   ")
        assert False, "Empty invite code must be rejected"
    except ValueError as exc:
        assert str(exc) == "Invite code is required"

    assert session.state == "waiting_invite_code"


def test_child_registration_rejects_empty_name():
    session = RegistrationSession(telegram_id=123456789)

    session.start_child_registration()
    session.set_invite_code("ABCD-2345")

    try:
        session.complete_child_registration("   ")
        assert False, "Empty child name must be rejected"
    except ValueError as exc:
        assert str(exc) == "Child name is required"

    assert session.state == "waiting_child_name"


def test_parent_registration_accepts_login():
    session = RegistrationSession(telegram_id=123456789)

    session.start_parent_registration()
    session.set_login("parent@example.com")

    assert session.login == "parent@example.com"
    assert session.state == "waiting_password"


def test_parent_registration_completes_without_storing_password():
    session = RegistrationSession(telegram_id=123456789)

    session.start_parent_registration()
    session.set_login("parent@example.com")

    result = session.complete_parent_registration("SecretPassword123")

    assert result == {
        "telegram_id": 123456789,
        "login": "parent@example.com",
        "password": "SecretPassword123",
    }
    assert not hasattr(session, "password")


def test_parent_registration_cannot_complete_without_login():
    session = RegistrationSession(telegram_id=123456789)

    session.start_parent_registration()

    try:
        session.complete_parent_registration("SecretPassword123")
        assert False, "Registration must not complete without login"
    except ValueError as exc:
        assert str(exc) == "Login is required"


def test_parent_registration_is_completed_after_password():
    session = RegistrationSession(telegram_id=123456789)

    session.start_parent_registration()
    session.set_login("parent@example.com")

    result = session.complete_parent_registration("SecretPassword123")

    assert session.state == "completed"
    assert result["telegram_id"] == 123456789
    assert result["login"] == "parent@example.com"
    assert result["password"] == "SecretPassword123"


def test_parent_registration_rejects_empty_login():
    session = RegistrationSession(telegram_id=123456789)

    session.start_parent_registration()

    try:
        session.set_login("")
        assert False, "Empty login must be rejected"
    except ValueError as exc:
        assert str(exc) == "Login is required"


def test_parent_registration_rejects_empty_password():
    session = RegistrationSession(telegram_id=123456789)

    session.start_parent_registration()
    session.set_login("parent@example.com")

    try:
        session.complete_parent_registration("")
        assert False, "Empty password must be rejected"
    except ValueError as exc:
        assert str(exc) == "Password is required"


def test_parent_registration_cannot_complete_before_login_step():
    session = RegistrationSession(telegram_id=123456789)

    session.start_parent_registration()

    try:
        session.complete_parent_registration("SecretPassword123")
        assert False, "Registration must not complete before login step"
    except ValueError as exc:
        assert str(exc) == "Login is required"

    assert session.state == "waiting_login"


def test_parent_registration_moves_to_waiting_password_after_login():
    session = RegistrationSession(telegram_id=123456789)

    session.start_parent_registration()
    session.set_login("parent@example.com")

    assert session.state == "waiting_password"
    assert session.login == "parent@example.com"


def test_parent_registration_result_is_ready_for_backend():
    session = RegistrationSession(telegram_id=123456789)

    session.start_parent_registration()
    session.set_login("parent@example.com")

    result = session.complete_parent_registration("SecretPassword123")

    assert result == {
        "telegram_id": 123456789,
        "login": "parent@example.com",
        "password": "SecretPassword123",
    }
