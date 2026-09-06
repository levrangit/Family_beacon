"""PySide6 pairing window for the Device Agent."""

from __future__ import annotations

from typing import Callable, Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


FAMILY_BEACON_BACKGROUND = "#f7f9ff"
FAMILY_BEACON_SURFACE = "#ffffff"
FAMILY_BEACON_PRIMARY = "#005bbf"
FAMILY_BEACON_OUTLINE = "#c1c6d6"
FAMILY_BEACON_TEXT = "#181c20"
FAMILY_BEACON_TEXT_VARIANT = "#414754"


class DevicePairingWindow(QDialog):
    """Family Beacon Agent pairing window.

    The Agent supplies the temporary pairing code. The user only provides a
    friendly device name; operating-system selection is intentionally absent
    because the Agent determines the platform itself.
    """

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

        self.setWindowTitle("Подключение устройства")
        self.setModal(True)
        self.setFixedSize(460, 430)
        self.setStyleSheet(
            f"""
            QDialog {{
                background: {FAMILY_BEACON_BACKGROUND};
                color: {FAMILY_BEACON_TEXT};
            }}
            QLabel {{
                color: {FAMILY_BEACON_TEXT};
                font-family: 'Segoe UI';
            }}
            QLabel#title {{
                color: {FAMILY_BEACON_TEXT};
                font-size: 20pt;
                font-weight: 700;
            }}
            QLabel#instructions {{
                color: {FAMILY_BEACON_TEXT_VARIANT};
                font-size: 10pt;
                line-height: 1.4;
            }}
            QLabel#qr_placeholder {{
                background: {FAMILY_BEACON_SURFACE};
                color: {FAMILY_BEACON_TEXT_VARIANT};
                border: 1px solid {FAMILY_BEACON_OUTLINE};
                border-radius: 14px;
                font-size: 10pt;
            }}
            QLabel#pairing_code {{
                color: {FAMILY_BEACON_PRIMARY};
                font-family: 'Segoe UI';
                font-size: 18pt;
                font-weight: 700;
                letter-spacing: 2px;
            }}
            QLabel#field_label {{
                color: {FAMILY_BEACON_TEXT_VARIANT};
                font-size: 9pt;
                font-weight: 600;
            }}
            QLineEdit#device_name {{
                background: {FAMILY_BEACON_SURFACE};
                color: {FAMILY_BEACON_TEXT};
                border: 1px solid {FAMILY_BEACON_OUTLINE};
                border-radius: 10px;
                padding: 9px 12px;
                font-family: 'Segoe UI';
                font-size: 10pt;
            }}
            QLineEdit#device_name:focus {{
                border: 2px solid {FAMILY_BEACON_PRIMARY};
                padding: 8px 11px;
            }}
            QPushButton#cancel, QPushButton#complete {{
                border-radius: 10px;
                padding: 9px 16px;
                min-height: 20px;
                font-family: 'Segoe UI';
                font-size: 10pt;
                font-weight: 600;
            }}
            QPushButton#cancel {{
                background: {FAMILY_BEACON_SURFACE};
                color: {FAMILY_BEACON_TEXT};
                border: 1px solid {FAMILY_BEACON_OUTLINE};
            }}
            QPushButton#cancel:hover {{
                background: {FAMILY_BEACON_BACKGROUND};
            }}
            QPushButton#complete {{
                background: {FAMILY_BEACON_PRIMARY};
                color: white;
                border: 1px solid {FAMILY_BEACON_PRIMARY};
            }}
            QPushButton#complete:hover {{
                background: #1a73e8;
                border-color: #1a73e8;
            }}
            """
        )

        self._build(child_name)

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
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(14)

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
        actions.setSpacing(10)
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
        """Display a temporary pairing code supplied by the Agent."""
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
    """Create and show the Agent pairing window."""
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
