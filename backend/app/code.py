from hashlib import sha256
from secrets import choice


_CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


def generate_code() -> str:
    first = "".join(choice(_CODE_ALPHABET) for _ in range(4))
    second = "".join(choice(_CODE_ALPHABET) for _ in range(4))
    return f"{first}-{second}"


def hash_code(code: str) -> str:
    return sha256(code.encode("utf-8")).hexdigest()
