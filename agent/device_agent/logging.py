"""Safe logging setup for Device Agent 0.1.0."""

import logging


LOGGER_NAME = "family_beacon.device_agent"


def setup_logging(level: str = "INFO") -> logging.Logger:
    """Configure and return the Agent logger."""

    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
        logger.addHandler(handler)

    logger.propagate = False
    return logger
