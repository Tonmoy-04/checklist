from __future__ import annotations

import sqlite3
from datetime import datetime, timezone


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class SettingsRepository:
    """Persist validated local application preferences."""

    DEFAULTS = {
        "theme": "dark",
        "reminders_enabled": "true",
        "default_reminder_offset_minutes": "0",
        "notify_missed_reminders": "true",
    }

    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def get(self, key: str, default: str | None = None) -> str | None:
        row = self.connection.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
        return row["value"] if row is not None else default

    def set(self, key: str, value: str) -> None:
        with self.connection:
            self.connection.execute(
                "INSERT INTO settings(key, value, updated_at) VALUES (?, ?, ?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at",
                (key, value, _now()),
            )

    def all(self) -> dict[str, str]:
        return {row["key"]: row["value"] for row in self.connection.execute("SELECT key, value FROM settings")}

    def seed_defaults(self) -> None:
        for key, value in self.DEFAULTS.items():
            if self.get(key) is None:
                self.set(key, value)
