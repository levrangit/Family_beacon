"""Bootstrap credential handling for an installed Family Beacon Agent."""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import secrets


AGENT_SECRET_PREFIX = "fb_agent_"


@dataclass(frozen=True)
class AgentBootstrapCredentials:
    agent_secret: str


def generate_agent_secret() -> str:
    """Generate a unique secret for this Agent installation."""
    return AGENT_SECRET_PREFIX + secrets.token_urlsafe(32)


def default_credentials_path() -> Path:
    """Return the per-machine credential path used by the MVP Agent."""
    program_data = os.getenv("PROGRAMDATA")
    if program_data:
        return Path(program_data) / "FamilyBeacon" / "agent_credentials.json"
    return Path.home() / ".family_beacon" / "agent_credentials.json"


def load_or_create_credentials(path: Path | None = None) -> AgentBootstrapCredentials:
    """Load the Agent secret or create it once for this installation."""
    credentials_path = path or default_credentials_path()
    if credentials_path.exists():
        payload = json.loads(credentials_path.read_text(encoding="utf-8"))
        secret = str(payload.get("agent_secret") or "")
        if not secret.startswith(AGENT_SECRET_PREFIX):
            raise ValueError("Stored Agent secret is invalid")
        return AgentBootstrapCredentials(agent_secret=secret)

    credentials_path.parent.mkdir(parents=True, exist_ok=True)
    credentials = AgentBootstrapCredentials(agent_secret=generate_agent_secret())
    temporary_path = credentials_path.with_suffix(".tmp")
    temporary_path.write_text(
        json.dumps({"agent_secret": credentials.agent_secret}, indent=2),
        encoding="utf-8",
    )
    os.replace(temporary_path, credentials_path)
    return credentials
