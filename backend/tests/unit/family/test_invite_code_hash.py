from app.invite_code import hash_invite_code


def test_hash_invite_code_returns_string():
    result = hash_invite_code("7K4M-92QX")

    assert isinstance(result, str)


def test_hash_invite_code_is_not_plaintext():
    code = "7K4M-92QX"

    result = hash_invite_code(code)

    assert result != code


def test_hash_invite_code_is_deterministic():
    code = "7K4M-92QX"

    first = hash_invite_code(code)
    second = hash_invite_code(code)

    assert first == second


def test_different_invite_codes_have_different_hashes():
    first = hash_invite_code("7K4M-92QX")
    second = hash_invite_code("ABCD-2345")

    assert first != second
