import getpass
import pytest

from device_agent.executor import CommandExecutor


def test_get_device_state_is_supported():
    assert "get_device_state" in CommandExecutor.SUPPORTED_COMMANDS


def test_get_device_state_rejected_on_non_windows(monkeypatch):
    monkeypatch.setattr(
        "device_agent.executor.platform.system",
        lambda: "Linux",
    )

    executor = CommandExecutor()

    with pytest.raises(
        RuntimeError,
        match="supported only on Windows",
    ):
        executor.execute("get_device_state")


def test_get_device_state_returns_device_information(monkeypatch):
    monkeypatch.setattr(
        "device_agent.executor.platform.system",
        lambda: "Windows",
    )

    monkeypatch.setattr(
        "device_agent.executor.platform.node",
        lambda: "FAMILY-PC",
    )

    monkeypatch.setattr(
        "getpass.getuser",
        lambda: "child",
    )

    executor = CommandExecutor()

    result = executor.execute("get_device_state")

    assert result == {
        "status": "online",
        "platform": "Windows",
        "hostname": "FAMILY-PC",
        "username": "child",
    }
