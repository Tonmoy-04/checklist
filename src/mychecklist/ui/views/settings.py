"""Settings screen for local preferences and safe backup/restore actions."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from datetime import datetime
from typing import Any

from mychecklist.database.backup import backup_database, restore_database
from mychecklist.repositories.settings_repository import SettingsRepository
from mychecklist.theme import DARK_COLORS, FONTS, SPACING


class SettingsView:
    def __init__(self, parent: Any, ctk_module: Any, *, settings: SettingsRepository,
                 connection: Any, database_path: Path, backup_directory: Path,
                 on_error: Callable[[str], None],
                 choose_restore_file: Callable[[], Path | None] | None = None,
                 confirm_restore: Callable[[], bool] | None = None) -> None:
        self.ctk = ctk_module
        self.settings = settings
        self.connection = connection
        self.database_path = database_path
        self.backup_directory = backup_directory
        self.on_error = on_error
        self.choose_restore_file = choose_restore_file
        self.confirm_restore = confirm_restore or (lambda: False)
        self.container = self.ctk.CTkFrame(parent, fg_color=DARK_COLORS["bg.canvas"])
        self.container.grid(row=0, column=0, sticky="nsew")
        self._build()

    def _build(self) -> None:
        self.container.grid_columnconfigure(1, weight=1)
        self._label("Settings", FONTS["display"], 0)
        self._label("Theme", FONTS["body"], 1)
        self.theme = self.ctk.CTkComboBox(self.container, values=["dark", "light"])
        self.theme.set(self.settings.get("theme", "dark"))
        self.theme.grid(row=1, column=1, padx=SPACING["space.3"], pady=SPACING["space.2"], sticky="ew")
        self._label("Reminders", FONTS["body"], 2)
        self.reminders = self.ctk.CTkComboBox(self.container, values=["enabled", "disabled"])
        self.reminders.set("enabled" if self.settings.get("reminders_enabled", "true") == "true" else "disabled")
        self.reminders.grid(row=2, column=1, padx=SPACING["space.3"], pady=SPACING["space.2"], sticky="ew")
        self.ctk.CTkButton(self.container, text="Save settings", command=self.save).grid(
            row=3, column=0, columnspan=2, padx=SPACING["space.3"], pady=SPACING["space.4"], sticky="ew"
        )
        self.ctk.CTkButton(self.container, text="Create backup", command=self.backup).grid(
            row=4, column=0, columnspan=2, padx=SPACING["space.3"], pady=SPACING["space.2"], sticky="ew"
        )
        self.ctk.CTkButton(self.container, text="Restore backup", command=self.restore).grid(
            row=5, column=0, columnspan=2, padx=SPACING["space.3"], pady=SPACING["space.2"], sticky="ew"
        )

    def _label(self, text: str, font: Any, row: int) -> None:
        self.ctk.CTkLabel(self.container, text=text, font=font, text_color=DARK_COLORS["text.primary"]).grid(
            row=row, column=0, padx=SPACING["space.3"], pady=SPACING["space.2"], sticky="w"
        )

    def save(self) -> None:
        try:
            theme = self.theme.get()
            if theme not in {"dark", "light"}:
                raise ValueError("unsupported theme")
            self.settings.set("theme", theme)
            self.settings.set("reminders_enabled", "true" if self.reminders.get() == "enabled" else "false")
        except Exception as error:
            self.on_error(str(error))

    def backup(self) -> None:
        try:
            destination = self.backup_directory / "checklist-backup.db"
            backup_database(self.connection, destination)
        except Exception as error:
            self.on_error(str(error))

    def restore(self) -> None:
        if self.choose_restore_file is None:
            self.on_error("Choose a validated backup file to restore.")
            return
        source = self.choose_restore_file()
        if source is None or not self.confirm_restore():
            return
        try:
            pre_restore = self.backup_directory / (
                f"pre-restore-{datetime.now().strftime('%Y%m%d-%H%M%S')}.db"
            )
            restore_database(source, self.database_path, pre_restore)
        except Exception as error:
            self.on_error(str(error))
