"""Family Beacon visual tokens and Qt stylesheet for the Device Agent."""

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
