from telegram_bot.child_menu import CHILD_MENU_TEXT, format_child_menu
from telegram_bot.handlers.start import PARENT_MENU_TEXT
from telegram_bot.version import get_project_version


def test_project_version_matches_root_version_file():
    from pathlib import Path

    version_file = Path(__file__).resolve().parents[2] / "VERSION"
    assert get_project_version() == version_file.read_text(encoding="utf-8").strip()


def test_parent_menu_shows_project_version_without_v_prefix():
    assert PARENT_MENU_TEXT == f"🌟 Семейный маяк · {get_project_version()}"
    assert f"v{get_project_version()}" not in PARENT_MENU_TEXT


def test_child_menu_shows_project_version_without_v_prefix():
    assert CHILD_MENU_TEXT == f"🌟 Семейный маяк · {get_project_version()}"
    assert format_child_menu({"name": "Мария"}) == (
        f"🌟 Семейный маяк · {get_project_version()}\n\nПривет, Мария!"
    )
    assert f"v{get_project_version()}" not in CHILD_MENU_TEXT
