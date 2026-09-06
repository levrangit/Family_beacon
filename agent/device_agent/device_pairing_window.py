"""PySide6 pairing window for the Device Agent."""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QApplication, QDialog, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget

from .ui.theme import PAIRING_WINDOW_QSS
from .ui.titlebar import TitleBar

ICON_PATH = Path(__file__).resolve().parent / "tray" / "assets" / "family_beacon.svg"
WINDOW_TITLE = "Подключение устройства"


class DevicePairingWindow(QDialog):
    """Family Beacon Agent pairing window with a custom title bar."""

    def __init__(
        self,
        *,
        child_name: str,
        pairing_code: str = "",
        on_complete: Optional[Callable[[str, str], None]] = None,
        on_cancel: Optional[Callable[[], None]] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._on_complete = on_complete
        self._on_cancel = on_cancel
        self._pairing_code = pairing_code
        self._copy_notification_text = ""

        self.setObjectName("pairing_window")
        self.setWindowTitle(WINDOW_TITLE)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        self.setFixedSize(460, 340)
        self.setStyleSheet(PAIRING_WINDOW_QSS)

        self._build()

    @property
    def pairing_code(self) -> str:
        return self._pairing_code

    @property
    def device_name_edit(self) -> QLineEdit:
        return self._device_name_edit

    @property
    def cancel_button(self) -> QPushButton:
        return self._cancel_button

    @property
    def complete_button(self) -> QPushButton:
        return self._complete_button

    def _build(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        container = QWidget(self)
        container.setObjectName("pairing_container")
        outer.addWidget(container)

        root = QVBoxLayout(container)
        root.setContentsMargins(28, 0, 28, 24)
        root.setSpacing(14)

        titlebar = TitleBar(self, str(ICON_PATH), WINDOW_TITLE)
        root.addWidget(titlebar)

        title = QLabel(WINDOW_TITLE)
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(title)

        instructions = QLabel(
            "1. Установите приложение «Семейный маяк» на устройство\n"
            "2. Введите код сопряжения:"
        )
        instructions.setObjectName("instructions")
        instructions.setWordWrap(True)
        root.addWidget(instructions)

        self._code_label = QLabel(self._pairing_code or "Код сопряжения появится здесь")
        self._code_label.setObjectName("pairing_code")
        self._code_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._code_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self._code_label.mousePressEvent = self._copy_pairing_code
        root.addWidget(self._code_label)

        name_label = QLabel("Название устройства")
        name_label.setObjectName("field_label")
        root.addWidget(name_label)

        self._device_name_edit = QLineEdit("Новый компьютер")
        self._device_name_edit.setObjectName("device_name")
        root.addWidget(self._device_name_edit)

        actions = QHBoxLayout()
        actions.addStretch()

        self._cancel_button = QPushButton("Отмена")
        self._cancel_button.setObjectName("cancel")
        self._cancel_button.clicked.connect(self._cancel)
        actions.addWidget(self._cancel_button)

        self._complete_button = QPushButton("Завершить регистрацию")
        self._complete_button.setObjectName("complete")
        self._complete_button.setDefault(True)
        self._complete_button.clicked.connect(self._complete)
        actions.addWidget(self._complete_button)

        root.addLayout(actions)

    def show_pairing(self, pairing_code: str) -> None:
        self._pairing_code = pairing_code
        self._code_label.setText(pairing_code)

    def _copy_pairing_code(self, _event: QMouseEvent) -> None:
        QApplication.clipboard().setText(self._pairing_code)
        self._copy_notification_text = "Код скопирован"

    def _complete(self) -> None:
        device_name = self._device_name_edit.text().strip() or "Новое устройство"
        if self._on_complete is not None:
            self._on_complete(device_name, self._pairing_code)
        self.accept()

    def _cancel(self) -> None:
        if self._on_cancel is not None:
            self._on_cancel()
        self.reject()


def open_device_pairing_window(
    *,
    child_name: str,
    pairing_code: str = "",
    on_complete: Optional[Callable[[str, str], None]] = None,
    on_cancel: Optional[Callable[[], None]] = None,
    parent: Optional[QWidget] = None,
) -> DevicePairingWindow:
    window = DevicePairingWindow(
        child_name=child_name,
        pairing_code=pairing_code,
        on_complete=on_complete,
        on_cancel=on_cancel,
        parent=parent,
    )
    window.show()
    window.raise_()
    window.activateWindow()
    return window


def main() -> int:
    """Run the pairing window as a standalone visual preview."""
    app = QApplication.instance() or QApplication()
    window = DevicePairingWindow(child_name="Ребёнок", pairing_code="123-456")
    window.show()
    window.raise_()
    window.activateWindow()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
