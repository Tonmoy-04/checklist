from __future__ import annotations

import sqlite3
from datetime import datetime, timezone


BUILTIN_CATEGORIES = ("Personal", "University", "Learning", "Work", "Health", "Other")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class CategoryRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def seed_builtins(self) -> None:
        with self.connection:
            self.connection.executemany(
                "INSERT OR IGNORE INTO categories(name, is_builtin, created_at) VALUES (?, 1, ?)",
                ((name, _now()) for name in BUILTIN_CATEGORIES),
            )

    def list(self, include_archived: bool = False) -> list[sqlite3.Row]:
        query = "SELECT * FROM categories"
        if not include_archived:
            query += " WHERE is_archived = 0"
        return list(self.connection.execute(query + " ORDER BY name"))

    def create(self, name: str) -> int:
        cleaned = name.strip()
        if not 1 <= len(cleaned) <= 50:
            raise ValueError("category name must be 1-50 characters")
        with self.connection:
            cursor = self.connection.execute(
                "INSERT INTO categories(name, is_builtin, created_at) VALUES (?, 0, ?)",
                (cleaned, _now()),
            )
        return int(cursor.lastrowid)

    def archive(self, category_id: int) -> None:
        with self.connection:
            self.connection.execute("UPDATE categories SET is_archived = 1 WHERE id = ?", (category_id,))
