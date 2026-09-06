"""Reusable Family Beacon custom Qt title bar."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QMouseEvent
from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QPushButton, QWidget


class TitleBar(QWidget):
    """Custom title bar with native window movement and controls."""

    def __init__(self, window: QDialog, icon_path: str, title: str) -> None:
        super().__init__(window)
        self._window = window
        self.setObjectName("titlebar")
        self.setFixedHeight(42)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 6, 8, 4)
        layout.setSpacing(8)

        icon = QLabel(self)
        icon.setObjectName("titlebar_icon")
        icon.setPixmap(QIcon(icon_path).pixmap(22, 22))
        icon.setFixedSize(22, 22)
        layout.addWidget(icon)

        title_label = QLabel(title, self)
        title_label.setObjectName("titlebar_title")
        layout.addWidget(title_label)
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
