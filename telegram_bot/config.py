from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()


def _required(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Required environment variable is missing: {name}")
    return value


API_ID = int(_required("TELEGRAM_API_ID"))
API_HASH = _required("TELEGRAM_API_HASH")
BOT_TOKEN = _required("TELEGRAM_BOT_TOKEN")

BACKEND_URL = os.getenv("FAMILY_BEACON_BACKEND_URL", "http://127.0.0.1:8000")
TELEGRAM_BOT_SHARED_SECRET = _required("TELEGRAM_BOT_SHARED_SECRET")
SESSION_PATH = os.getenv("TELEGRAM_SESSION_PATH", "telegram_bot.session")
