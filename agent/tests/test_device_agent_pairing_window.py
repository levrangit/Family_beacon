"""TDD tests for the Device Agent PySide6 pairing window."""

from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QLabel, QLineEdit, QPushButton, QWidget

from agent.device_agent.device_pairing_window import (
    DevicePairingWindow,
    open_device_pairing_window,
)
from agent.device_agent.ui.theme import (
    BACKGROUND,
    FONT_FAMILY,
    ON_SURFACE,
    OUTLINE_VARIANT,
    PAIRING_WINDOW_QSS,
    PRIMARY,
    SURFACE,
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
        "2. Введите код сопряжения:"
    ]
    window.close()


def test_pairing_window_uses_family_beacon_light_background() -> None:
    _app()
    window = DevicePairingWindow(child_name="Алексей")
    stylesheet = window.styleSheet()
    assert "QDialog#pairing_window" in stylesheet
    assert f"background: {BACKGROUND}" in stylesheet
    window.close()


def test_pairing_window_title_uses_large_bold_font() -> None:
    _app()
    window = DevicePairingWindow(child_name="Алексей")
    stylesheet = window.styleSheet()
    assert "QLabel#title" in stylesheet
    assert "font-size: 20pt" in stylesheet
    assert "font-weight: 700" in stylesheet
    assert f"font-family: {FONT_FAMILY}" in stylesheet
    window.close()


def test_pairing_code_is_visually_emphasized_with_family_beacon_blue() -> None:
    _app()
    window = DevicePairingWindow(child_name="Алексей", pairing_code="123-456")
    stylesheet = window.styleSheet()
    assert "QLabel#pairing_code" in stylesheet
    assert f"color: {PRIMARY}" in stylesheet
    assert "font-size: 22pt" in stylesheet
    assert "font-weight: 700" in stylesheet
    assert window.findChild(QLabel, "pairing_code").font().underline()
    window.close()


def test_device_name_field_has_family_beacon_surface_and_outline() -> None:
    _app()
    window = DevicePairingWindow(child_name="Алексей")
    stylesheet = window.styleSheet()
    assert "QLineEdit#device_name" in stylesheet
    assert f"background: {SURFACE}" in stylesheet
    assert f"color: {ON_SURFACE}" in stylesheet
    assert f"border: 1px solid {OUTLINE_VARIANT}" in stylesheet
    assert "border-radius: 10px" in stylesheet
    window.close()


def test_complete_button_uses_family_beacon_primary_style() -> None:
    _app()
    window = DevicePairingWindow(child_name="Алексей")
    button = window.complete_button
    stylesheet = window.styleSheet()
    assert button.isDefault()
    assert "QPushButton#complete" in stylesheet
    assert f"background: {PRIMARY}" in stylesheet
    assert f"border: 1px solid {PRIMARY}" in stylesheet
    assert "border-radius: 10px" in stylesheet
    window.close()


def test_cancel_button_uses_secondary_visual_style() -> None:
    _app()
    window = DevicePairingWindow(child_name="Алексей")
    stylesheet = window.styleSheet()
    assert "QPushButton#cancel" in stylesheet
    assert f"background: {SURFACE}" in stylesheet
    assert f"border: 1px solid {OUTLINE_VARIANT}" in stylesheet
    assert "border-radius: 10px" in stylesheet
    window.close()


def test_pairing_window_theme_matches_shared_qss() -> None:
    _app()
    window = DevicePairingWindow(child_name="Алексей")
    assert window.styleSheet() == PAIRING_WINDOW_QSS
    window.close()


def test_pairing_window_uses_shared_rounded_container_style() -> None:
    _app()
    window = DevicePairingWindow(child_name="Алексей")
    stylesheet = window.styleSheet()
    assert "QWidget#pairing_container" in stylesheet
    assert "border-radius: 16px" in stylesheet
    window.close()


def test_pairing_window_uses_custom_frameless_window() -> None:
    _app()
    window = DevicePairingWindow(child_name="Алексей")
    assert window.windowFlags() & Qt.WindowType.FramelessWindowHint
    window.close()


def test_pairing_window_has_custom_titlebar() -> None:
    _app()
    window = DevicePairingWindow(child_name="Алексей")
    titlebar = window.findChild(QWidget, "titlebar")
    assert titlebar is not None
    window.close()


def test_custom_titlebar_has_family_beacon_icon() -> None:
    _app()
    window = DevicePairingWindow(child_name="Алексей")
    icon = window.findChild(QLabel, "titlebar_icon")
    assert icon is not None
    assert not icon.pixmap().isNull()
    window.close()


def test_custom_titlebar_has_window_title() -> None:
    _app()
    window = DevicePairingWindow(child_name="Алексей")
    title = window.findChild(QLabel, "titlebar_title")
    assert title is not None
    assert title.text() == "Подключение устройства"
    window.close()


def test_custom_titlebar_has_window_control_buttons() -> None:
    _app()
    window = DevicePairingWindow(child_name="Алексей")
    assert window.findChild(QPushButton, "titlebar_minimize") is not None
    assert window.findChild(QPushButton, "titlebar_maximize") is not None
    assert window.findChild(QPushButton, "titlebar_close") is not None
    window.close()


def test_custom_minimize_button_minimizes_window() -> None:
    _app()
    window = DevicePairingWindow(child_name="Алексей")
    window.show()
    _app().processEvents()
    button = window.findChild(QPushButton, "titlebar_minimize")
    assert button is not None
    button.click()
    _app().processEvents()
    assert window.isMinimized()
    window.close()


def test_custom_maximize_button_toggles_maximized_state() -> None:
    _app()
    window = DevicePairingWindow(child_name="Алексей")
    window.show()
    _app().processEvents()
    button = window.findChild(QPushButton, "titlebar_maximize")
    assert button is not None
    button.click()
    _app().processEvents()
    assert window.isMaximized()
    button.click()
    _app().processEvents()
    assert not window.isMaximized()
    window.close()


def test_custom_close_button_closes_window() -> None:
    _app()
    window = DevicePairingWindow(child_name="Алексей")
    window.show()
    _app().processEvents()
    button = window.findChild(QPushButton, "titlebar_close")
    assert button is not None
    button.click()
    _app().processEvents()
    assert not window.isVisible()


def test_titlebar_exposes_system_move_handler() -> None:
    _app()
    window = DevicePairingWindow(child_name="Алексей")
    titlebar = window.findChild(QWidget, "titlebar")
    assert titlebar is not None
    assert hasattr(titlebar, "start_system_move")
    window.close()


def test_pairing_code_is_clickable_link() -> None:
    _app()
    window = DevicePairingWindow(child_name="Алексей", pairing_code="123-456")
    code = window.findChild(QLabel, "pairing_code")
    assert code is not None
    assert code.text() == "123-456"
    assert code.cursor().shape() == Qt.CursorShape.PointingHandCursor
    assert code.font().underline()
    window.close()


def test_pairing_code_click_copies_code_to_clipboard() -> None:
    app = _app()
    window = DevicePairingWindow(child_name="Алексей", pairing_code="123-456")
    code = window.findChild(QLabel, "pairing_code")
    assert code is not None
    window.show()
    app.processEvents()
    app.clipboard().clear()
    QTest.mouseClick(code, Qt.MouseButton.LeftButton)
    app.processEvents()
    assert app.clipboard().text() == "123-456"
    window.close()


def test_pairing_code_click_shows_copied_message() -> None:
    app = _app()
    window = DevicePairingWindow(child_name="Алексей", pairing_code="123-456")
    code = window.findChild(QLabel, "pairing_code")
    notification = window.findChild(QLabel, "copy_notification")
    assert code is not None
    assert notification is not None
    assert not notification.isVisible()
    window.show()
    app.processEvents()
    QTest.mouseClick(code, Qt.MouseButton.LeftButton)
    app.processEvents()
    assert notification.text() == "Код скопирован"
    assert notification.isVisible()
    window.close()


def test_pairing_window_does_not_contain_qr_code() -> None:
    _app()
    window = DevicePairingWindow(child_name="Алексей", pairing_code="123-456")
    visible_labels = [widget.text() for widget in window.findChildren(QLabel)]
    assert not any("QR" in text or "QR-код" in text for text in visible_labels)
    assert "qr_placeholder" not in window.styleSheet()
    window.close()


def test_pairing_window_instructions_do_not_mention_qr_code() -> None:
    _app()
    window = DevicePairingWindow(child_name="Алексей")
    instructions = [
        widget.text()
        for widget in window.findChildren(QLabel)
        if "Установите приложение" in widget.text()
    ]
    assert instructions == [
        "1. Установите приложение «Семейный маяк» на устройство\n"
        "2. Введите код сопряжения:"
    ]
    window.close()
