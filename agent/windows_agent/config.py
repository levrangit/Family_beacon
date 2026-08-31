from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"

load_dotenv(ENV_FILE)


FAMILY_BEACON_API_URL = os.getenv(
    "FAMILY_BEACON_API_URL",
    ""
).strip()

ACCESS_TOKEN_JWT = os.getenv(
    "ACCESS_TOKEN_JWT",
    ""
).strip()

DEVICE_TOKEN = os.getenv(
    "DEVICE_TOKEN",
    ""
).strip()

FAMILY_BEACON_REQUEST_TIMEOUT = float(
    os.getenv(
        "FAMILY_BEACON_REQUEST_TIMEOUT",
        "10",
    )
)


def validate_config() -> None:
    errors: list[str] = []

    if not FAMILY_BEACON_API_URL:
        errors.append("FAMILY_BEACON_API_URL is not configured")

    if not DEVICE_TOKEN:
        errors.append("DEVICE_TOKEN is not configured")

    if FAMILY_BEACON_REQUEST_TIMEOUT <= 0:
        errors.append(
            "FAMILY_BEACON_REQUEST_TIMEOUT must be greater than 0"
        )

    if errors:
        raise RuntimeError(
            "Windows Agent configuration error:\n- "
            + "\n- ".join(errors)
        )
