from secrets import choice


_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


def generate_invite_code() -> str:
    first = "".join(choice(_ALPHABET) for _ in range(4))
    second = "".join(choice(_ALPHABET) for _ in range(4))
    return f"{first}-{second}"


import hashlib


def hash_invite_code(code: str) -> str:
    return hashlib.sha256(code.encode("utf-8")).hexdigest()
