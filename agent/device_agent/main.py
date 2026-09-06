"""Entry point for Device Agent 0.1.0."""

from .config import load_config
from .identity import collect_identity
from .logging import setup_logging


def main() -> int:
    """Run the minimal identity-only Agent lifecycle."""

    config = load_config()
    logger = setup_logging(config.log_level)

    logger.info("Starting Device Agent %s", config.agent_version)
    identity = collect_identity(config.agent_version)

    logger.info(
        "Identity collected: platform=%s hostname=%s username=%s session=%s",
        identity.platform,
        identity.hostname,
        identity.os_username,
        identity.os_session_identity,
    )
    logger.info("Device Agent %s finished successfully", config.agent_version)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
