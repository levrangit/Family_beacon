"""TDD tests for the Device Agent PySide6 pairing window."""

from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtGui import QFont, QPalette
from PySide6.QtWidgets import QApplication, QLineEdit, QPushButton, QWidget, QLabel

from agent.device_agent.device_pairing_window import (
    DevicePairingWindow,
    open_device_pairing_window,
)


def _app() -> QApplication:
    return QApplication.instance() or QApplication([])


def test_pairing_window_can_be_created() -> None:
    _app()
    window = DevicePairingWindow(child_name="Алексей")

    assert window is not None

    window.close()


def test_pairing_window_has_device_name_field() -> None:
    _app()
    window = DevicePairingWindow(child_name="Алексей")

    fields = window.findChildren(QLineEdit)

    assert len(fields) == 1
    assert fields[0].objectName() == "device_name"

    window.close()


def test_pairing_window_has_pairing_code() -> None:
    _app()
    window = DevicePairingWindow(child_name="Алексей", pairing_code="123-456")

    assert window.pairing_code == "123-456"

    window.close()


def test_pairing_window_does_not_offer_os_selection() -> None:
    _app()
    window = DevicePairingWindow(child_name="Алексей")

    visible_text = window.windowTitle() + " " + " ".join(
        widget.text() for widget in window.findChildren(QPushButton)
    )

    assert "Windows" not in visible_text
    assert "macOS" not in visible_text
    assert "Linux" not in visible_text

    window.close()


def test_pairing_window_has_cancel_button() -> None:
    _app()
    window = DevicePairingWindow(child_name="Алексей")

    buttons = {button.text(): button for button in window.findChildren(QPushButton)}

    assert "Отмена" in buttons

    window.close()


def test_pairing_window_has_complete_registration_button() -> None:
    _app()
    window = DevicePairingWindow(child_name="Алексей")

    buttons = {button.text(): button for button in window.findChildren(QPushButton)}

    assert "Завершить регистрацию" in buttons

    window.close()


def test_cancel_closes_window_and_calls_callback() -> None:
    _app()
    cancelled: list[bool] = []
    window = DevicePairingWindow(
        child_name="Алексей",
        on_cancel=lambda: cancelled.append(True),
    )

    window.cancel_button.click()
    _app().processEvents()

    assert cancelled == [True]
    assert not window.isVisible()


def test_complete_registration_closes_window_and_returns_data() -> None:
    _app()
    completed: list[tuple[str, str]] = []
    window = DevicePairingWindow(
        child_name="Алексей",
        pairing_code="123-456",
        on_complete=lambda device_name, pairing_code: completed.append(
            (device_name, pairing_code)
        ),
    )
    window.device_name_edit.setText("Компьютер Алексея")

    window.complete_button.click()
    _app().processEvents()

    assert completed == [("Компьютер Алексея", "123-456")]
    assert not window.isVisible()


def test_pairing_window_accepts_qt_parent() -> None:
    _app()
    parent = QWidget()
    window = DevicePairingWindow(child_name="Алексей", parent=parent)

    assert window.parentWidget() is parent

    window.close()
    parent.close()


def test_open_device_pairing_window_creates_and_shows_window() -> None:
    _app()
    window = open_device_pairing_window(
        child_name="Алексей",
        pairing_code="123-456",
    )
    _app().processEvents()

    assert isinstance(window, DevicePairingWindow)
    assert window.isVisible()
    assert window.pairing_code == "123-456"

    window.close()


def test_show_pairing_updates_pairing_code() -> None:
    _app()
    window = DevicePairingWindow(child_name="Алексей")

    window.show_pairing("654-321")

    assert window.pairing_code == "654-321"
    assert window.findChild(QPushButton, "complete") is not None

    window.close()


def test_complete_uses_default_name_when_device_name_is_blank() -> None:
    _app()
    completed: list[tuple[str, str]] = []
    window = DevicePairingWindow(
        child_name="Алексей",
        pairing_code="123-456",
        on_complete=lambda device_name, pairing_code: completed.append(
            (device_name, pairing_code)
        ),
    )
    window.device_name_edit.setText("   ")

    window.complete_button.click()
    _app().processEvents()

    assert completed == [("Новое устройство", "123-456")]
    window.close()


def test_pairing_window_has_requested_title_without_child_name() -> None:
    _app()
    window = DevicePairingWindow(child_name="Алексей")

    assert window.windowTitle() == "Подключение устройства"

    window.close()


def test_pairing_window_has_requested_heading_without_child_name() -> None:
    _app()
    window = DevicePairingWindow(child_name="Алексей")

    headings = [
        widget.text()
        for widget in window.findChildren(QLabel)
        if widget.objectName() == "title"
    ]

    assert headings == ["Подключение устройства"]

    window.close()


def test_pairing_window_has_requested_instructions() -> None:
    _app()
    window = DevicePairingWindow(child_name="Алексей")

    instructions = [
        widget.text()
        for widget in window.findChildren(QLabel)
        if "Установите приложение" in widget.text()
    ]

    assert instructions == [
        "1. Установите приложение «Семейный маяк» на устройство\n"
        "2. Введите код сопряжения или отсканируйте QR-код:"
    ]

    window.close()


def test_pairing_window_uses_family_beacon_light_background() -> None:
    _app()
    window = DevicePairingWindow(child_name="Алексей")

    background = window.palette().color(QPalette.ColorRole.Window).name()

    assert background == "#f7f9ff"

    window.close()


def test_pairing_window_title_uses_large_bold_font() -> None:
    _app()
    window = DevicePairingWindow(child_name="Алексей")

    title = window.findChild(QLabel, "title")
    assert title is not None

    font: QFont = title.font()
    assert font.pointSize() >= 18
    assert font.bold()

    window.close()


def test_pairing_code_is_visually_emphasized_with_family_beacon_blue() -> None:
    _app()
    window = DevicePairingWindow(child_name="Алексей", pairing_code="123-456")

    code = window.findChild(QLabel, "pairing_code")
    assert code is not None

    assert code.palette().color(QPalette.ColorRole.WindowText).name() == "#005bbf"
    assert code.font().bold()

    window.close()


def test_device_name_field_has_family_beacon_surface_and_outline() -> None:
    _app()
    window = DevicePairingWindow(child_name="Алексей")

    field = window.device_name_edit

    assert field.palette().color(QPalette.ColorRole.Base).name() == "#ffffff"
    assert "#c1c6d6" in field.styleSheet()

    window.close()


def test_complete_button_uses_family_beacon_primary_style() -> None:
    _app()
    window = DevicePairingWindow(child_name="Алексей")

    button = window.complete_button

    assert button.isDefault()
    assert "#005bbf" in button.styleSheet()
    assert "border-radius" in button.styleSheet()

    window.close()


def test_cancel_button_uses_secondary_visual_style() -> None:
    _app()
    window = DevicePairingWindow(child_name="Алексей")

    button = window.cancel_button

    assert "background" in button.styleSheet()
    assert "border-radius" in button.styleSheet()

    window.close()
