"""PySide6 pairing window for the Device Agent."""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Optional

from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QIcon, QMouseEvent
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from .ui.theme import PAIRING_WINDOW_QSS, PRIMARY, SURFACE

ICON_PATH = Path(__file__).resolve().parent / "tray" / "assets" / "family_beacon.svg"


class _TitleBar(QWidget):
    """Custom title bar that delegates window movement to the native Qt API."""

    def __init__(self, window: QDialog) -> None:
        super().__init__(window)
        self._window = window
        self.setObjectName("titlebar")
        self.setFixedHeight(42)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 6, 8, 4)
        layout.setSpacing(8)

        icon = QLabel(self)
        icon.setObjectName("titlebar_icon")
        icon.setPixmap(QIcon(str(ICON_PATH)).pixmap(22, 22))
        icon.setFixedSize(22, 22)
        layout.addWidget(icon)

        title = QLabel("Подключение устройства", self)
        title.setObjectName("titlebar_title")
        layout.addWidget(title)
        layout.addStretch()

        minimize = self._button("—", "titlebar_minimize")
        minimize.clicked.connect(window.showMinimized)
        layout.addWidget(minimize)

        maximize = self._button("□", "titlebar_maximize")
        maximize.clicked.connect(self._toggle_maximize)
        layout.addWidget(maximize)

        close = self._button("×", "titlebar_close")
        close.clicked.connect(window.close)
        layout.addWidget(close)

    @staticmethod
    def _button(text: str, object_name: str) -> QPushButton:
        button = QPushButton(text)
        button.setObjectName(object_name)
        button.setFixedSize(34, 30)
        button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        return button

    def _toggle_maximize(self) -> None:
        if self._window.isMaximized():
            self._window.showNormal()
        else:
            self._window.showMaximized()

    def start_system_move(self) -> bool:
        """Request a native window move for the current pointer position."""
        handle = self._window.windowHandle()
        return bool(handle and handle.startSystemMove())

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_system_move()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._toggle_maximize()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)


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

        self.setObjectName("pairing_window")
        self.setWindowTitle("Подключение устройства")
        self.setWindowFlags(
            Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        self.setFixedSize(460, 472)
        self.setStyleSheet(PAIRING_WINDOW_QSS + self._titlebar_qss())

        self._build(child_name)

    @staticmethod
    def _titlebar_qss() -> str:
        return f"""
QWidget#pairing_container {{
    background: #f7f9ff;
    border-radius: 16px;
}}

QWidget#titlebar {{
    background: transparent;
}}

QLabel#titlebar_title {{
    color: #181c20;
    font-family: "Segoe UI";
    font-size: 10pt;
    font-weight: 600;
}}

QPushButton#titlebar_minimize,
QPushButton#titlebar_maximize,
QPushButton#titlebar_close {{
    background: transparent;
    color: #414754;
    border: none;
    border-radius: 7px;
    font-family: "Segoe UI";
    font-size: 13pt;
    font-weight: 400;
    padding: 0;
}}

QPushButton#titlebar_minimize:hover,
QPushButton#titlebar_maximize:hover {{
    background: #ebeef4;
}}

QPushButton#titlebar_close:hover {{
    background: #ba1a1a;
    color: #ffffff;
}}
"""

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

    def _build(self, child_name: str) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        container = QWidget(self)
        container.setObjectName("pairing_container")
        outer.addWidget(container)

        root = QVBoxLayout(container)
        root.setContentsMargins(28, 0, 28, 24)
        root.setSpacing(14)

        titlebar = _TitleBar(self)
        root.addWidget(titlebar)

        title = QLabel("Подключение устройства")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(title)

        instructions = QLabel(
            "1. Установите приложение «Семейный маяк» на устройство\n"
            "2. Введите код сопряжения или отсканируйте QR-код:"
        )
        instructions.setObjectName("instructions")
        instructions.setWordWrap(True)
        root.addWidget(instructions)

        qr = QLabel("QR\nбудет создан\nздесь")
        qr.setObjectName("qr_placeholder")
        qr.setAlignment(Qt.AlignmentFlag.AlignCenter)
        qr.setFixedSize(120, 120)
        root.addWidget(qr, alignment=Qt.AlignmentFlag.AlignCenter)

        self._code_label = QLabel(self._pairing_code or "Код сопряжения появится здесь")
        self._code_label.setObjectName("pairing_code")
        self._code_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
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
