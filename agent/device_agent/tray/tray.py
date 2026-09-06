"""Minimal cross-platform Device Agent Tray skeleton."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Callable

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QSystemTrayIcon

from .menu import build_tray_menu

TRAY_ICON_PATH = Path(__file__).resolve().parent / "assets" / "family_beacon.svg"


class DeviceAgentTray:
    """Own the Tray UI lifecycle without talking to the backend."""

    def __init__(self, app: QApplication, *, on_register: Callable[[], None] | None = None) -> None:
        self._app = app
        self._on_register = on_register or self._registration_placeholder
        self.tray = QSystemTrayIcon(app)
        self.tray.setToolTip("Family Beacon — Device Agent")
        self.tray.setIcon(QIcon(str(TRAY_ICON_PATH)))
        self.tray.setContextMenu(build_tray_menu(self._on_register, self._quit))

    def show(self) -> None:
        """Show the Tray icon and start normal Tray operation."""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            raise RuntimeError("System tray is not available on this system")
        self.tray.show()

    def _registration_placeholder(self) -> None:
        """Stage A placeholder for the future registration flow."""
        self.tray.showMessage(
            "Family Beacon",
            "Регистрация будет подключена на следующем этапе.",
            QSystemTrayIcon.Information,
            3000,
        )

    def _quit(self) -> None:
        """Stop only the Tray application; the Agent Service is independent."""
        self.tray.hide()
        self._app.quit()


def main() -> int:
    """Run the minimal Device Agent Tray."""
    app = QApplication(sys.argv)
    app.setApplicationName("Family Beacon Device Agent")
    app.setQuitOnLastWindowClosed(False)
    tray = DeviceAgentTray(app)
    tray.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
