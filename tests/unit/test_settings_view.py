import sqlite3
from pathlib import Path

from mychecklist.repositories.settings_repository import SettingsRepository
from mychecklist.ui.views.settings import SettingsView


class Widget:
    def __init__(self, parent=None, **kwargs):
        self.parent = parent
        self.kwargs = kwargs
        self.value = ""
        self.destroyed = False

    def grid(self, **kwargs):
        self.grid_options = kwargs

    def grid_columnconfigure(self, *args, **kwargs):
        pass

    def grid_rowconfigure(self, *args, **kwargs):
        pass

    def set(self, value):
        self.value = value

    def get(self):
        return self.value

    def destroy(self):
        self.destroyed = True


class FakeCtk:
    CTkFrame = Widget
    CTkScrollableFrame = Widget
    CTkLabel = Widget
    CTkComboBox = Widget
    CTkButton = Widget


def test_settings_renders_scrollable_content_and_persists_values(tmp_path: Path):
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.execute(
        "CREATE TABLE settings (key TEXT PRIMARY KEY, value TEXT NOT NULL, updated_at TEXT NOT NULL)"
    )
    repository = SettingsRepository(connection)
    repository.set("theme", "dark")
    repository.set("reminders_enabled", "true")
    errors = []

    view = SettingsView(
        Widget(), FakeCtk, settings=repository, connection=connection,
        database_path=tmp_path / "checklist.db",
        backup_directory=tmp_path / "backups", on_error=errors.append,
    )

    assert view.content.kwargs["fg_color"] == "transparent"
    assert view.theme.get() == "dark"
    assert view.reminders.get() == "enabled"
    view.theme.set("light")
    view.reminders.set("disabled")
    view.save()

    assert repository.get("theme") == "light"
    assert repository.get("reminders_enabled") == "false"
    assert errors == []
