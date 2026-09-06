"""Minimal runtime configuration for Device Agent 0.1.0."""

from dataclasses import dataclass


@dataclass(frozen=True)
class AgentConfig:
    """Configuration intentionally limited to MVP runtime settings."""

    agent_version: str = "0.1.0"
    environment: str = "local"
    log_level: str = "INFO"


def load_config() -> AgentConfig:
    """Return the default MVP configuration.

    Device identity, credentials, pairing and backend settings are deliberately
    not part of the 0.1.0 configuration surface yet.
    """

    return AgentConfig()
