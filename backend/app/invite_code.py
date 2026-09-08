from .code import generate_code, hash_code


def generate_invite_code() -> str:
    return generate_code()


def hash_invite_code(code: str) -> str:
    return hash_code(code)
