from tests_backend.support.auth.users import AuthTestUser


def test_auth_test_user_keeps_identity_and_role():
    user = AuthTestUser(
        name="parent",
        email="unit-parent@example.com",
        password="unit-password",
        expected_role="parent",
        user_id="unit-user-id",
    )

    assert user.name == "parent"
    assert user.email == "unit-parent@example.com"
    assert user.password == "unit-password"
    assert user.expected_role == "parent"
    assert user.user_id == "unit-user-id"
