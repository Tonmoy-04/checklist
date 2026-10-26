"""Settings screen for local preferences and safe backup/restore actions."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from datetime import datetime
from typing import Any

from mychecklist.database.backup import backup_database, restore_database
from mychecklist.repositories.settings_repository import SettingsRepository
from mychecklist.theme import COMPONENTS, DARK_COLORS, FONTS, SPACING


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
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        self._build()

    def _build(self) -> None:
        self.content = self.ctk.CTkScrollableFrame(self.container, fg_color="transparent")
        self.content.grid(row=0, column=0, padx=SPACING["space.5"], pady=SPACING["space.4"], sticky="nsew")
        self.content.grid_columnconfigure(1, weight=1)
        self._label("Settings", FONTS["display"], 0, 2)
        self._label("Manage appearance, reminders, and local data.", FONTS["body"], 1, 2, DARK_COLORS["text.secondary"])
        self._section_label("Preferences", 2)
        self._label("Theme", FONTS["label"], 3)
        self.theme = self.ctk.CTkComboBox(self.content, values=["dark", "light"], **COMPONENTS["input"])
        self.theme.set(self.settings.get("theme", "dark"))
        self.theme.grid(row=3, column=1, padx=SPACING["space.3"], pady=SPACING["space.2"], sticky="ew")
        self._label("Reminders", FONTS["label"], 4)
        self.reminders = self.ctk.CTkComboBox(self.content, values=["enabled", "disabled"], **COMPONENTS["input"])
        self.reminders.set("enabled" if self.settings.get("reminders_enabled", "true") == "true" else "disabled")
        self.reminders.grid(row=4, column=1, padx=SPACING["space.3"], pady=SPACING["space.2"], sticky="ew")
        self._section_label("Data safety", 6)
        self.ctk.CTkButton(self.content, text="Save settings", command=self.save, **COMPONENTS["primary_button"]).grid(
            row=5, column=0, columnspan=2, padx=SPACING["space.3"], pady=SPACING["space.4"], sticky="ew"
        )
        self.ctk.CTkButton(self.content, text="Create backup", command=self.backup, **COMPONENTS["secondary_button"]).grid(
            row=7, column=0, columnspan=2, padx=SPACING["space.3"], pady=SPACING["space.2"], sticky="ew"
        )
        self.ctk.CTkButton(self.content, text="Restore backup", command=self.restore, **COMPONENTS["secondary_button"]).grid(
            row=8, column=0, columnspan=2, padx=SPACING["space.3"], pady=SPACING["space.2"], sticky="ew"
        )
        self._section_label("About", 9)
        self._label(
            "MyChecklist stores tasks locally under %LOCALAPPDATA%\\MyChecklist. "
            "Reminders are delivered while the app is open.",
            FONTS["body_small"], 10, 2, DARK_COLORS["text.secondary"],
        )

    def _label(self, text: str, font: Any, row: int, columnspan: int = 1,
               color: str | None = None) -> None:
        self.ctk.CTkLabel(self.content, text=text, font=font, text_color=color or DARK_COLORS["text.primary"]).grid(
            row=row, column=0, columnspan=columnspan, padx=SPACING["space.3"],
            pady=SPACING["space.2"], sticky="w"
        )

    def _section_label(self, text: str, row: int) -> None:
        self.ctk.CTkLabel(
            self.content, text=text.upper(), font=FONTS["caption"],
            text_color=DARK_COLORS["accent.primary"],
        ).grid(row=row, column=0, columnspan=2, padx=SPACING["space.3"], pady=(SPACING["space.5"], SPACING["space.1"]), sticky="w")

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
