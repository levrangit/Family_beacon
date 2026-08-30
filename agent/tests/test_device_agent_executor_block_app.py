import pytest

from device_agent.executor import CommandExecutor


def test_block_app_is_supported():
    assert "block_app" in CommandExecutor.SUPPORTED_COMMANDS


def test_block_app_rejected_on_non_windows(monkeypatch):
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
            "block_app",
            {"app": "notepad.exe"},
        )


def test_block_app_requires_app():
    executor = CommandExecutor()

    with pytest.raises(
        ValueError,
        match="app",
    ):
        executor.execute(
            "block_app",
            {},
        )


def test_block_app_rejects_empty_app():
    executor = CommandExecutor()

    with pytest.raises(
        ValueError,
        match="app",
    ):
        executor.execute(
            "block_app",
            {"app": ""},
        )


@pytest.mark.skipif(
    __import__("platform").system() != "Windows",
    reason="Requires a real Windows agent",
)
def test_block_app_returns_blocked_application():
    executor = CommandExecutor()

    result = executor.execute(
        "block_app",
        {"app": "notepad.exe"},
    )

    assert result == {
        "status": "app_blocked",
        "app": "notepad.exe",
    }
