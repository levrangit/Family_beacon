"""Family Beacon visual tokens and Qt styles for the Device Agent."""

from __future__ import annotations

# Keep these values aligned with frontend/src/index.css.
PRIMARY = "#005bbf"
PRIMARY_CONTAINER = "#1a73e8"
BACKGROUND = "#f7f9ff"
SURFACE = "#ffffff"
SURFACE_CONTAINER = "#ebeef4"
ON_SURFACE = "#181c20"
ON_SURFACE_VARIANT = "#414754"
OUTLINE = "#727785"
OUTLINE_VARIANT = "#c1c6d6"
SECONDARY = "#006e2c"
ERROR = "#ba1a1a"

FONT_FAMILY = "Segoe UI"

PAIRING_WINDOW_QSS = f"""
QDialog#pairing_window {{
    background: {BACKGROUND};
    color: {ON_SURFACE};
    font-family: {FONT_FAMILY};
}}

QLabel#title {{
    color: {ON_SURFACE};
    font-family: {FONT_FAMILY};
    font-size: 20pt;
    font-weight: 700;
}}

QLabel#instructions {{
    color: {ON_SURFACE_VARIANT};
    font-family: {FONT_FAMILY};
    font-size: 10pt;
}}

QLabel#qr_placeholder {{
    background: {SURFACE};
    color: {ON_SURFACE_VARIANT};
    border: 1px solid {OUTLINE_VARIANT};
    border-radius: 16px;
    font-family: {FONT_FAMILY};
    font-size: 10pt;
}}

QLabel#pairing_code {{
    color: {PRIMARY};
    font-family: {FONT_FAMILY};
    font-size: 22pt;
    font-weight: 700;
    letter-spacing: 2px;
}}

QLabel#field_label {{
    color: {ON_SURFACE};
    font-family: {FONT_FAMILY};
    font-size: 9pt;
    font-weight: 600;
}}

QLineEdit#device_name {{
    background: {SURFACE};
    color: {ON_SURFACE};
    border: 1px solid {OUTLINE_VARIANT};
    border-radius: 10px;
    padding: 10px 12px;
    font-family: {FONT_FAMILY};
    font-size: 10pt;
}}

QLineEdit#device_name:focus {{
    border: 2px solid {PRIMARY};
    padding: 9px 11px;
}}

QPushButton#cancel, QPushButton#complete {{
    min-height: 38px;
    padding: 0 16px;
    border-radius: 10px;
    font-family: {FONT_FAMILY};
    font-size: 10pt;
    font-weight: 600;
}}

QPushButton#cancel {{
    background: {SURFACE};
    color: {PRIMARY};
    border: 1px solid {OUTLINE_VARIANT};
}}

QPushButton#cancel:hover {{
    background: {SURFACE_CONTAINER};
}}

QPushButton#complete {{
    background: {PRIMARY};
    color: {SURFACE};
    border: 1px solid {PRIMARY};
}}

QPushButton#complete:hover {{
    background: {PRIMARY_CONTAINER};
    border-color: {PRIMARY_CONTAINER};
}}

QPushButton#complete:pressed {{
    background: {PRIMARY_CONTAINER};
}}

QPushButton#complete:disabled {{
    background: {SURFACE_CONTAINER};
    color: {ON_SURFACE_VARIANT};
    border-color: {OUTLINE_VARIANT};
}}
"""

FAMILY_BEACON_QSS = f"""
QMenu {{
    background: {SURFACE};
    color: {ON_SURFACE};
    border: 1px solid {OUTLINE_VARIANT};
    border-radius: 10px;
    padding: 6px;
    font-family: {FONT_FAMILY};
    font-size: 10pt;
}}

QMenu::item {{
    padding: 8px 28px 8px 12px;
    border-radius: 7px;
}}

QMenu::item:selected {{
    background: #d8e2ff;
    color: {ON_SURFACE};
}}

QMenu::separator {{
    height: 1px;
    background: {OUTLINE_VARIANT};
    margin: 5px 8px;
}}
"""


def apply_family_beacon_theme(app) -> None:
    """Apply the shared Family Beacon Qt visual language to the Agent UI."""
    app.setStyleSheet(FAMILY_BEACON_QSS)
