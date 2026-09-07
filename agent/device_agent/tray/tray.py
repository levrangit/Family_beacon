"""Device Agent Tray UI connected to the Windows Service through IPC."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Callable

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMessageBox, QSystemTrayIcon

from ..device_pairing_window import DevicePairingWindow, open_device_pairing_window
from ..ipc.named_pipe_client import NamedPipeIPCClient
from ..ipc.protocol import REGISTRATION_CANCEL, REGISTRATION_START
from ..ui.theme import apply_family_beacon_theme
from .menu import build_tray_menu

TRAY_ICON_PATH = Path(__file__).resolve().parent / "assets" / "family_beacon.svg"


class DeviceAgentTray:
    """Own the Tray UI and communicate with the Agent Service through IPC."""

    def __init__(self, app: QApplication, *, on_register: Callable[[], None] | None = None) -> None:
        self._app = app
        self._pairing_window: DevicePairingWindow | None = None
        self._registration_request_id: str | None = None
        self._on_register = on_register or self._start_registration
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

    def _start_registration(self) -> None:
        """Ask the Service to create a local registration attempt."""
        if self._pairing_window is not None and self._pairing_window.isVisible():
            self._pairing_window.raise_()
            self._pairing_window.activateWindow()
            return

        client = NamedPipeIPCClient()
        try:
            client.connect()
            response = client.request({"type": REGISTRATION_START})
        except ConnectionError as exc:
            QMessageBox.warning(
                None,
                "Family Beacon",
                "Сервис Family Beacon недоступен. Запустите службу и повторите попытку.",
            )
            return
        finally:
            client.close()

        if not response.get("ok") or not response.get("registration_code"):
            QMessageBox.warning(
                None,
                "Family Beacon",
                "Не удалось начать регистрацию устройства.",
            )
            return

        self._registration_request_id = response.get("request_id")
        self._pairing_window = open_device_pairing_window(
            child_name="Ребёнок",
            pairing_code=str(response["registration_code"]),
            on_cancel=self._cancel_registration,
        )
        self._pairing_window.finished.connect(self._release_pairing_window)

    def _cancel_registration(self) -> None:
        """Tell the Service to cancel the active local registration attempt."""
        client = NamedPipeIPCClient()
        try:
            client.connect()
            client.request({"type": REGISTRATION_CANCEL})
        except ConnectionError:
            pass
        finally:
            client.close()
        self._registration_request_id = None

    def _release_pairing_window(self, _result: int | None = None) -> None:
        """Forget the pairing window after it has been closed."""
        self._pairing_window = None

    def _registration_placeholder(self) -> None:
        """Compatibility alias for the current registration test seam."""
        self._start_registration()

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
    """Run the Device Agent Tray."""
    app = QApplication(sys.argv)
    app.setApplicationName("Family Beacon Device Agent")
    app.setQuitOnLastWindowClosed(False)
    apply_family_beacon_theme(app)
    tray = DeviceAgentTray(app)
    tray.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
