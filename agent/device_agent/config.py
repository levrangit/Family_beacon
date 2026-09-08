"""Runtime configuration for the Family Beacon Device Agent."""

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class AgentConfig:
    """Runtime settings required by the Device Agent service."""

    agent_version: str = "0.1.0"
    environment: str = "local"
    log_level: str = "INFO"
    backend_url: str = "http://127.0.0.1:8000"
    registration_poll_interval_seconds: int = 10


def load_config() -> AgentConfig:
    """Load runtime settings from environment with safe local defaults."""
    backend_url = os.getenv(
        "FAMILY_BEACON_BACKEND_URL",
        "http://127.0.0.1:8000",
    ).rstrip("/")
    poll_interval = int(
        os.getenv("FAMILY_BEACON_PAIRING_POLL_INTERVAL_SECONDS", "10")
    )
    if poll_interval <= 0:
        raise ValueError("FAMILY_BEACON_PAIRING_POLL_INTERVAL_SECONDS must be positive")

    return AgentConfig(
        backend_url=backend_url,
        registration_poll_interval_seconds=poll_interval,
    )
