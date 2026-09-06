"""Minimal Windows user interface for Device Agent registration."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from .registration import RegistrationCoordinator


class AgentUI:
    """Small standalone UI for starting a device registration attempt."""

    def __init__(self, coordinator: RegistrationCoordinator | None = None) -> None:
        self.coordinator = coordinator or RegistrationCoordinator()
        self.root = tk.Tk()
        self.root.title("Family Beacon")
        self.root.resizable(False, False)

        frame = ttk.Frame(self.root, padding=24)
        frame.grid(row=0, column=0)

        ttk.Label(
            frame,
            text="Family Beacon",
            font=("Segoe UI", 16, "bold"),
        ).grid(row=0, column=0, pady=(0, 8))

        self.status = ttk.Label(
            frame,
            text="Устройство не зарегистрировано.",
            justify="center",
        )
        self.status.grid(row=1, column=0, pady=(0, 16))

        self.register_button = ttk.Button(
            frame,
            text="Регистрация",
            command=self._start_registration,
        )
        self.register_button.grid(row=2, column=0)

        self.code_label = ttk.Label(frame, text="", font=("Segoe UI", 20, "bold"))
        self.code_label.grid(row=3, column=0, pady=(16, 8))

        self.cancel_button = ttk.Button(
            frame,
            text="Отмена",
            command=self._cancel_registration,
        )
        self.cancel_button.grid(row=4, column=0)
        self.cancel_button.grid_remove()

    def _start_registration(self) -> None:
        request = self.coordinator.start()
        self.status.configure(
            text="Введите этот временный код в Telegram\nдля начала регистрации устройства."
        )
        self.code_label.configure(text=request.registration_code)
        self.register_button.configure(state="disabled")
        self.cancel_button.grid()

    def _cancel_registration(self) -> None:
        self.coordinator.cancel()
        self.status.configure(text="Регистрация отменена.")
        self.code_label.configure(text="")
        self.register_button.configure(state="normal")
        self.cancel_button.grid_remove()

    def run(self) -> None:
        """Run the UI event loop."""
        self.root.mainloop()
