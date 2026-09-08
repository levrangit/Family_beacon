from datetime import datetime, timezone

from telegram_bot.agent_installation_handlers import (
    format_agent_installation,
    parent_family_buttons_with_installation,
)


def test_format_agent_installation_shows_code_and_expiry():
    text = format_agent_installation(
        {
            "installation_code": "ABCD-2345",
            "expires_at": "2026-09-08T12:30:00+00:00",
        }
    )

    assert "ABCD-2345" in text
    assert "08.09.2026 12:30 UTC" in text
    assert "один раз" in text


def test_family_buttons_include_agent_installation():
    buttons = parent_family_buttons_with_installation(
        {
            "name": "Моя семья",
            "children": [],
        }
    )

    callbacks = [button.data for row in buttons for button in row]
    assert b"parent:agent_installation" in callbacks
