import os
from pathlib import Path

from dotenv import load_dotenv


AGENT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = AGENT_DIR.parents[1]
BACKEND_ENV_FILE = PROJECT_DIR / "backend" / ".env"
VERSION_FILE = PROJECT_DIR / "VERSION"

load_dotenv(BACKEND_ENV_FILE)


BACKEND_URL = os.getenv(
    "FAMILY_BEACON_BACKEND_URL",
    "http://127.0.0.1:8000",
)

DEVICE_TOKEN = os.getenv(
    "FAMILY_BEACON_DEVICE_TOKEN",
    "",
)


def _read_agent_version() -> str:
    configured_version = os.getenv("FAMILY_BEACON_AGENT_VERSION")
    if configured_version and configured_version.strip():
        return configured_version.strip()

    try:
        version = VERSION_FILE.read_text(encoding="utf-8").strip()
    except OSError:
        version = ""

    return version or "0.1.0"


AGENT_VERSION = _read_agent_version()

POLL_INTERVAL_SECONDS = int(
    os.getenv(
        "FAMILY_BEACON_POLL_INTERVAL_SECONDS",
        "5",
    )
)


HEARTBEAT_INTERVAL_SECONDS = int(
    os.getenv(
        "FAMILY_BEACON_HEARTBEAT_INTERVAL_SECONDS",
        "30",
    )
)
