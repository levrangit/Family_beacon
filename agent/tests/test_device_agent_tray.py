"""Tests for the minimal Device Agent Tray skeleton."""

from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from agent.device_agent.tray.menu import build_tray_menu


def test_tray_menu_contains_registration_and_quit() -> None:
    app = QApplication.instance() or QApplication([])

    menu = build_tray_menu(lambda: None, app.quit)
    assert [action.text() for action in menu.actions()] == [
        "Регистрация",
        "",
        "Выйти",
    ]

    menu.deleteLater()
