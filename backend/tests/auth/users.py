import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


BACKEND_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BACKEND_DIR / ".env")


@dataclass(frozen=True)
class AuthTestUser:
    name: str
    email: str
    password: str
    expected_role: str


def get_test_user(name: str) -> AuthTestUser:
    if name == "parent":
        email = os.getenv("TEST_PARENT_EMAIL") or os.getenv("TEST_EMAIL")
        password = os.getenv("TEST_PARENT_PASSWORD") or os.getenv("TEST_PASSWORD")

        if not email:
            raise RuntimeError(
                "TEST_PARENT_EMAIL or TEST_EMAIL is not set"
            )

        if not password:
            raise RuntimeError(
                "TEST_PARENT_PASSWORD or TEST_PASSWORD is not set"
            )

        return AuthTestUser(
            name="parent",
            email=email,
            password=password,
            expected_role="parent",
        )

    raise RuntimeError(f"Unknown test user: {name}")
