import os
from pathlib import Path

from dotenv import load_dotenv


AGENT_DIR = Path(__file__).resolve().parent
AGENT_ENV_FILE = AGENT_DIR.parent / ".env"

load_dotenv(AGENT_ENV_FILE)


BACKEND_URL = os.getenv(
    "FAMILY_BEACON_BACKEND_URL",
    "http://127.0.0.1:8000",
)

DEVICE_TOKEN = os.getenv(
    "FAMILY_BEACON_DEVICE_TOKEN",
    "",
)

POLL_INTERVAL_SECONDS = int(
    os.getenv(
        "FAMILY_BEACON_POLL_INTERVAL_SECONDS",
        "5",
    )
)
