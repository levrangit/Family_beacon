"""Device Agent pairing window.

This module provides the Agent-side registration window. The visual language is
based on the existing Family Beacon web AddDeviceModal, but this is a separate
Agent UI component and does not depend on the frontend application.

Stage 1 intentionally contains presentation and local interaction only. The
pairing code is supplied by the Agent through ``show_pairing`` and is not hard-coded
here. The device platform is supplied by the Agent as well, so the user does not
select an operating system in this window. Backend registration/approval is
deliberately not implemented in this module yet.
"""

from __future__ import annotations

import tkinter as tk
from typing import Callable, Optional


class DevicePairingWindow(tk.Toplevel):
    """Family Beacon Agent pairing window.

    The window mirrors the existing web pairing dialog:
    - title with the selected child's name;
    - instructions and pairing code;
    - device name field;
    - Cancel and Complete Pairing actions.

    The device platform is known by the Agent and is therefore not selected
    by the child. ``on_complete`` receives ``(device_name, pairing_code)``.
    The callback is intentionally injected so the Agent can later connect this
    UI to the real registration-request flow without coupling the window to the
    backend.
    """

    BG = "#f1f4fa"
    WHITE = "#ffffff"
    BORDER = "#dfe3e8"
    TEXT = "#181c20"
    MUTED = "#414754"
    PRIMARY = "#005bbf"
    PRIMARY_DARK = "#004493"

    def __init__(
        self,
        parent: tk.Misc,
        *,
        child_name: str,
        on_complete: Optional[Callable[[str, str], None]] = None,
        on_cancel: Optional[Callable[[], None]] = None,
    ) -> None:
        super().__init__(parent)
        self._on_complete = on_complete
        self._on_cancel = on_cancel
        self._pairing_code = ""
        self._device_name = tk.StringVar(value="Новый компьютер")

        self.title(f"Подключение устройства для {child_name}")
        self.resizable(False, False)
        self.configure(bg=self.BG)
        self.protocol("WM_DELETE_WINDOW", self._cancel)

        self._build(child_name)
        self._center(parent)

    def _build(self, child_name: str) -> None:
        outer = tk.Frame(self, bg=self.WHITE, highlightbackground=self.BORDER, highlightthickness=1)
        outer.pack(padx=12, pady=12)

        content = tk.Frame(outer, bg=self.WHITE, padx=24, pady=20)
        content.pack()

        header = tk.Frame(content, bg=self.WHITE)
        header.pack(fill="x", pady=(0, 14))
        tk.Label(header, text="▣", bg=self.WHITE, fg=self.PRIMARY, font=("Segoe UI", 18, "bold")).pack(side="left")
        tk.Label(
            header,
            text=f"Подключение устройства для {child_name}",
            bg=self.WHITE,
            fg=self.TEXT,
            font=("Segoe UI", 13, "bold"),
        ).pack(side="left", padx=(8, 0))
        tk.Button(
            header,
            text="×",
            command=self._cancel,
            relief="flat",
            bd=0,
            bg=self.WHITE,
            fg="#727785",
            activebackground=self.WHITE,
            activeforeground=self.TEXT,
            font=("Segoe UI", 13),
        ).pack(side="right")

        info = tk.Frame(content, bg=self.BG, padx=16, pady=14)
        info.pack(fill="x", pady=(0, 14))
        tk.Label(
            info,
            text="1. Установите приложение «Семейный маяк» на устройство ребенка.\n"
            "2. Введите код сопряжения или отсканируйте QR-код:",
            bg=self.BG,
            fg=self.MUTED,
            justify="center",
            font=("Segoe UI", 9),
        ).pack(pady=(0, 10))

        self._qr_placeholder = tk.Label(
            info,
            text="QR\nбудет создан\nздесь",
            width=12,
            height=6,
            bg=self.WHITE,
            fg=self.MUTED,
            relief="solid",
            bd=1,
            font=("Segoe UI", 9, "bold"),
        )
        self._qr_placeholder.pack(pady=(0, 10))

        self._code_label = tk.Label(
            info,
            text="Код сопряжения появится здесь",
            bg=self.WHITE,
            fg=self.PRIMARY,
            padx=12,
            pady=5,
            relief="solid",
            bd=1,
            font=("Consolas", 11, "bold"),
        )
        self._code_label.pack()

        name_frame = tk.Frame(content, bg=self.WHITE)
        name_frame.pack(fill="x", pady=(0, 14))
        tk.Label(
            name_frame,
            text="Название устройства",
            bg=self.WHITE,
            fg=self.MUTED,
            font=("Segoe UI", 9, "bold"),
        ).pack(anchor="w", pady=(0, 4))
        entry = tk.Entry(
            name_frame,
            textvariable=self._device_name,
            bg=self.BG,
            fg=self.TEXT,
            relief="solid",
            bd=1,
            font=("Segoe UI", 9),
        )
        entry.pack(fill="x", ipady=6)

        actions = tk.Frame(content, bg=self.WHITE)
        actions.pack(fill="x")
        tk.Button(
            actions,
            text="Отмена",
            command=self._cancel,
            relief="flat",
            bd=0,
            bg=self.WHITE,
            fg=self.MUTED,
            activebackground=self.BG,
            font=("Segoe UI", 9, "bold"),
        ).pack(side="right", padx=(0, 8))
        tk.Button(
            actions,
            text="Завершить сопряжение",
            command=self._complete,
            relief="flat",
            bd=0,
            bg=self.PRIMARY,
            fg=self.WHITE,
            activebackground=self.PRIMARY_DARK,
            activeforeground=self.WHITE,
            padx=14,
            pady=7,
            font=("Segoe UI", 9, "bold"),
        ).pack(side="right")

    def show_pairing(self, pairing_code: str) -> None:
        """Display a real temporary pairing code supplied by the Agent/backend."""
        self._pairing_code = pairing_code
        self._code_label.configure(text=pairing_code)

    def _complete(self) -> None:
        if self._on_complete is not None:
            self._on_complete(
                self._device_name.get().strip() or "Новое устройство",
                self._pairing_code,
            )

    def _cancel(self) -> None:
        if self._on_cancel is not None:
            self._on_cancel()
        self.destroy()

    def _center(self, parent: tk.Misc) -> None:
        self.update_idletasks()
        if parent.winfo_exists():
            x = parent.winfo_rootx() + max((parent.winfo_width() - self.winfo_width()) // 2, 0)
            y = parent.winfo_rooty() + max((parent.winfo_height() - self.winfo_height()) // 2, 0)
        else:
            x = (self.winfo_screenwidth() - self.winfo_width()) // 2
            y = (self.winfo_screenheight() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")


def open_device_pairing_window(
    parent: tk.Misc,
    *,
    child_name: str,
    pairing_code: str = "",
    on_complete: Optional[Callable[[str, str], None]] = None,
    on_cancel: Optional[Callable[[], None]] = None,
) -> DevicePairingWindow:
    """Open the Agent pairing window and optionally display its current code."""
    window = DevicePairingWindow(
        parent,
        child_name=child_name,
        on_complete=on_complete,
        on_cancel=on_cancel,
    )
    if pairing_code:
        window.show_pairing(pairing_code)
    window.transient(parent)
    window.grab_set()
    window.focus_set()
    return window
