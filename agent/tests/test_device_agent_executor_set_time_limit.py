import pytest

from device_agent.executor import CommandExecutor


def test_set_time_limit_is_supported():
    assert "set_time_limit" in CommandExecutor.SUPPORTED_COMMANDS


def test_set_time_limit_rejected_on_non_windows(monkeypatch):
    monkeypatch.setattr(
        "device_agent.executor.platform.system",
        lambda: "Linux",
    )

    executor = CommandExecutor()

    with pytest.raises(
        RuntimeError,
        match="supported only on Windows",
    ):
        executor.execute(
            "set_time_limit",
            {"minutes": 60},
        )


def test_set_time_limit_requires_minutes():
    executor = CommandExecutor()

    with pytest.raises(
        ValueError,
        match="minutes",
    ):
        executor.execute(
            "set_time_limit",
            {},
        )


def test_set_time_limit_requires_positive_minutes():
    executor = CommandExecutor()

    for minutes in (0, -1):
        with pytest.raises(
            ValueError,
            match="positive",
        ):
            executor.execute(
                "set_time_limit",
                {"minutes": minutes},
            )


def test_set_time_limit_requires_integer_minutes():
    executor = CommandExecutor()

    with pytest.raises(
        ValueError,
        match="integer",
    ):
        executor.execute(
            "set_time_limit",
            {"minutes": 30.5},
        )


def test_set_time_limit_returns_configured_limit(monkeypatch):
    monkeypatch.setattr(
        "device_agent.executor.platform.system",
        lambda: "Windows",
    )

    executor = CommandExecutor()

    result = executor.execute(
        "set_time_limit",
        {"minutes": 60},
    )

    assert result == {
        "status": "time_limit_set",
        "minutes": 60,
    }
