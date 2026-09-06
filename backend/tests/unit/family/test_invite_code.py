import re

import pytest

from app.invite_code import generate_invite_code


def test_generate_invite_code_has_expected_format():
    code = generate_invite_code()

    assert re.fullmatch(r"[A-Z2-9]{4}-[A-Z2-9]{4}", code)


def test_generate_invite_code_has_exact_length():
    code = generate_invite_code()

    assert len(code) == 9


def test_generate_invite_code_does_not_contain_ambiguous_characters():
    ambiguous_characters = set("0O1I")

    for _ in range(100):
        code = generate_invite_code()

        assert not ambiguous_characters.intersection(code)


def test_generate_invite_codes_are_not_all_identical():
    codes = {generate_invite_code() for _ in range(100)}

    assert len(codes) > 1


def test_generate_invite_code_contains_only_allowed_characters():
    allowed = set("ABCDEFGHJKLMNPQRSTUVWXYZ23456789-")

    for _ in range(100):
        code = generate_invite_code()

        assert set(code) <= allowed


def test_generate_invite_code_returns_string():
    code = generate_invite_code()

    assert isinstance(code, str)
