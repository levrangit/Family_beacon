from device_agent.config import AgentConfig, load_config


def test_load_config_returns_mvp_defaults() -> None:
    config = load_config()

    assert config == AgentConfig(
        agent_version="0.1.0",
        environment="local",
        log_level="INFO",
    )
