"""Context menu for the Device Agent Tray."""

from __future__ import annotations

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu


def build_tray_menu(on_register, on_restart, on_quit) -> QMenu:
    """Build the Device Agent Tray context menu."""
    menu = QMenu()

    register_action = QAction("Регистрация", menu)
    register_action.triggered.connect(on_register)
    menu.addAction(register_action)

    restart_action = QAction("Перезапуск", menu)
    restart_action.triggered.connect(on_restart)
    menu.addAction(restart_action)

    menu.addSeparator()

    quit_action = QAction("Выйти", menu)
    quit_action.triggered.connect(on_quit)
    menu.addAction(quit_action)

    return menu
