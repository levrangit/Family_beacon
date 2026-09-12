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
AUTHOR_TELEGRAM_ID = int(os.getenv("AUTHOR_TELEGRAM_ID", "0"))

MT_PROXY_HOST = os.getenv("TELEGRAM_MTPROTO_PROXY_HOST")
MT_PROXY_PORT = int(os.getenv("TELEGRAM_MTPROTO_PROXY_PORT", "0"))
MT_PROXY_SECRET = os.getenv("TELEGRAM_MTPROTO_PROXY_SECRET")

if any((MT_PROXY_HOST, MT_PROXY_PORT, MT_PROXY_SECRET)) and not all(
    (MT_PROXY_HOST, MT_PROXY_PORT, MT_PROXY_SECRET)
):
    raise RuntimeError(
        "MTProto proxy configuration is incomplete: "
        "TELEGRAM_MTPROTO_PROXY_HOST, TELEGRAM_MTPROTO_PROXY_PORT and "
        "TELEGRAM_MTPROTO_PROXY_SECRET must be set together"
    )
