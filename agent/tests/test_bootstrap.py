from pathlib import Path

from device_agent.bootstrap import (
    AGENT_SECRET_PREFIX,
    generate_agent_secret,
    load_or_create_credentials,
)


def test_generate_agent_secret_is_unique():
    first = generate_agent_secret()
    second = generate_agent_secret()

    assert first.startswith(AGENT_SECRET_PREFIX)
    assert second.startswith(AGENT_SECRET_PREFIX)
    assert first != second


def test_credentials_are_created_once(tmp_path: Path):
    path = tmp_path / "agent_credentials.json"

    first = load_or_create_credentials(path)
    second = load_or_create_credentials(path)

    assert first == second
    assert first.agent_secret.startswith(AGENT_SECRET_PREFIX)
