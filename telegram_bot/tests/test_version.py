from telegram_bot.child_menu import CHILD_MENU_TEXT, format_child_menu
from telegram_bot.handlers.start import PARENT_MENU_TEXT
from telegram_bot.version import get_project_version


def test_project_version_matches_root_version_file():
    assert get_project_version() == "0.1.0"


def test_parent_menu_shows_project_version_without_v_prefix():
    assert PARENT_MENU_TEXT == "🌟 Семейный маяк · 0.1.0"
    assert "v0.1.0" not in PARENT_MENU_TEXT


def test_child_menu_shows_project_version_without_v_prefix():
    assert CHILD_MENU_TEXT == "🌟 Семейный маяк · 0.1.0"
    assert format_child_menu({"name": "Мария"}) == "🌟 Семейный маяк · 0.1.0\n\nПривет, Мария!"
    assert "v0.1.0" not in CHILD_MENU_TEXT
