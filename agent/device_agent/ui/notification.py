"""Small transient notifications for the Device Agent UI."""

from __future__ import annotations

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QLabel, QWidget


class CopyNotification(QLabel):
    """Transient notification shown after copying the pairing code."""

    DISPLAY_DURATION_MS = 1600

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setObjectName("copy_notification")
        self.setText("Код скопирован")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hide()

        self._hide_timer = QTimer(self)
        self._hide_timer.setSingleShot(True)
        self._hide_timer.timeout.connect(self.hide)

    def show_message(self) -> None:
        """Show the notification briefly near the bottom of the parent."""
        parent = self.parentWidget()
        if parent is None:
            return

        self.adjustSize()
        margin = 20
        self.move(
            (parent.width() - self.width()) // 2,
            parent.height() - self.height() - margin,
        )
        self.raise_()
        self.show()
        self._hide_timer.start(self.DISPLAY_DURATION_MS)
