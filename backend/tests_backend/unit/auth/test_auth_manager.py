import os

import pytest

from tests.support.auth.users import get_test_user


def test_parent_test_user_is_loaded_from_environment():
    user = get_test_user("parent")

    expected_email = os.getenv("TEST_PARENT_EMAIL") or os.environ["TEST_EMAIL"]
    expected_password = os.getenv("TEST_PARENT_PASSWORD") or os.environ["TEST_PASSWORD"]

    assert user.email == expected_email
    assert user.password == expected_password
    assert user.expected_role == "parent"


def test_missing_parent_email_fails_clearly(monkeypatch):
    monkeypatch.delenv("TEST_PARENT_EMAIL", raising=False)
    monkeypatch.delenv("TEST_EMAIL", raising=False)

    with pytest.raises(RuntimeError, match="TEST_PARENT_EMAIL or TEST_EMAIL"):
        get_test_user("parent")


def test_missing_parent_password_fails_clearly(monkeypatch):
    monkeypatch.delenv("TEST_PARENT_PASSWORD", raising=False)
    monkeypatch.delenv("TEST_PASSWORD", raising=False)

    with pytest.raises(RuntimeError, match="TEST_PARENT_PASSWORD or TEST_PASSWORD"):
        get_test_user("parent")
