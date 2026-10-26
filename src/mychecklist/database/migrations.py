"""Versioned SQLite schema migrations."""
from __future__ import annotations

import sqlite3

CURRENT_SCHEMA_VERSION = 1


def migrate(connection: sqlite3.Connection) -> None:
    version = int(connection.execute("PRAGMA user_version").fetchone()[0])
    if version > CURRENT_SCHEMA_VERSION:
        raise RuntimeError(f"Unsupported database schema version: {version}")
    if version == CURRENT_SCHEMA_VERSION:
        return
    with connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL COLLATE NOCASE UNIQUE,
                is_builtin INTEGER NOT NULL CHECK (is_builtin IN (0, 1)),
                is_archived INTEGER NOT NULL DEFAULT 0 CHECK (is_archived IN (0, 1)),
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS task_series (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL CHECK (length(trim(title)) BETWEEN 1 AND 200),
                category_id INTEGER NOT NULL REFERENCES categories(id),
                priority TEXT NOT NULL CHECK (priority IN ('low', 'medium', 'high')),
                recurrence TEXT NOT NULL CHECK (recurrence IN ('none', 'daily', 'weekly', 'monthly')),
                interval_count INTEGER NOT NULL DEFAULT 1 CHECK (interval_count >= 1),
                start_date TEXT NOT NULL,
                due_time TEXT,
                is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS task_occurrences (
                id INTEGER PRIMARY KEY,
                series_id INTEGER NOT NULL REFERENCES task_series(id) ON DELETE RESTRICT,
                due_date TEXT NOT NULL,
                due_time TEXT,
                due_time_key TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL CHECK (status IN ('open', 'completed', 'cancelled')),
                completed_at TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                is_skipped INTEGER NOT NULL DEFAULT 0 CHECK (is_skipped IN (0, 1)),
                UNIQUE(series_id, due_date, due_time_key),
                CHECK ((status = 'completed' AND completed_at IS NOT NULL) OR
                       (status <> 'completed' AND completed_at IS NULL))
            );
            CREATE TABLE IF NOT EXISTS reminder_deliveries (
                id INTEGER PRIMARY KEY,
                occurrence_id INTEGER NOT NULL REFERENCES task_occurrences(id) ON DELETE CASCADE,
                reminder_offset_minutes INTEGER NOT NULL CHECK (reminder_offset_minutes >= 0),
                scheduled_for TEXT NOT NULL,
                attempted_at TEXT,
                delivered_at TEXT,
                status TEXT NOT NULL CHECK (status IN ('pending', 'delivered', 'failed', 'dismissed')),
                attempt_count INTEGER NOT NULL DEFAULT 0 CHECK (attempt_count >= 0),
                last_error_code TEXT,
                created_at TEXT NOT NULL,
                UNIQUE(occurrence_id, reminder_offset_minutes)
            );
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_occurrences_due_status ON task_occurrences(due_date, status);
            CREATE INDEX IF NOT EXISTS idx_occurrences_status_due ON task_occurrences(status, due_date, due_time);
            CREATE INDEX IF NOT EXISTS idx_occurrences_series_date ON task_occurrences(series_id, due_date);
            CREATE INDEX IF NOT EXISTS idx_reminder_status_schedule ON reminder_deliveries(status, scheduled_for);
            CREATE INDEX IF NOT EXISTS idx_series_category_active ON task_series(category_id, is_active);
            PRAGMA user_version = 1;
            """
        )


def integrity_check(connection: sqlite3.Connection) -> bool:
    return connection.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
