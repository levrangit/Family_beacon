"""Minimal cross-platform Device Agent Tray skeleton."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Callable

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QSystemTrayIcon

from ..device_pairing_window import DevicePairingWindow, open_device_pairing_window
from ..ui.theme import apply_family_beacon_theme
from .menu import build_tray_menu

TRAY_ICON_PATH = Path(__file__).resolve().parent / "assets" / "family_beacon.svg"


class DeviceAgentTray:
    """Own the Tray UI lifecycle without talking to the backend."""

    def __init__(self, app: QApplication, *, on_register: Callable[[], None] | None = None) -> None:
        self._app = app
        self._pairing_window: DevicePairingWindow | None = None
        self._on_register = on_register or self._open_pairing_window
        self.tray = QSystemTrayIcon(app)
        self.tray.setToolTip("Family Beacon — Device Agent")
        self.tray.setIcon(QIcon(str(TRAY_ICON_PATH)))
        self.tray.setContextMenu(
            build_tray_menu(self._on_register, self._restart, self._quit)
        )

    def show(self) -> None:
        """Show the Tray icon and start normal Tray operation."""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            raise RuntimeError("System tray is not available on this system")
        self.tray.show()

    def _open_pairing_window(self) -> None:
        """Open the local pairing window without contacting the backend."""
        if self._pairing_window is not None:
            if self._pairing_window.isVisible():
                self._pairing_window.raise_()
                self._pairing_window.activateWindow()
                return
            self._pairing_window = None

        self._pairing_window = open_device_pairing_window(
            child_name="Ребёнок",
            on_cancel=self._release_pairing_window,
        )
        self._pairing_window.finished.connect(self._release_pairing_window)

    def _release_pairing_window(self, _result: int | None = None) -> None:
        """Forget the pairing window after it has been closed."""
        self._pairing_window = None

    def _restart(self) -> None:
        """Start a new Tray process and then close the current process."""
        subprocess.Popen([sys.executable, *sys.argv], close_fds=True)
        self.tray.hide()
        self._app.quit()

    def _quit(self) -> None:
        """Stop only the Tray application; the Agent Service is independent."""
        self.tray.hide()
        self._app.quit()


def main() -> int:
    """Run the minimal Device Agent Tray."""
    app = QApplication(sys.argv)
    app.setApplicationName("Family Beacon Device Agent")
    app.setQuitOnLastWindowClosed(False)
    apply_family_beacon_theme(app)
    tray = DeviceAgentTray(app)
    tray.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
