"""Validated SQLite online backup and restore helpers."""
from __future__ import annotations

import sqlite3
from pathlib import Path

from mychecklist.database.connection import connect
from mychecklist.database.migrations import CURRENT_SCHEMA_VERSION, integrity_check


class BackupError(RuntimeError):
    pass


def backup_database(source: sqlite3.Connection, destination: str | Path) -> Path:
    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    target = sqlite3.connect(path)
    try:
        source.backup(target)
    finally:
        target.close()
    return path


def validate_backup(path: str | Path) -> None:
    backup_path = Path(path)
    if not backup_path.is_file():
        raise BackupError("backup file does not exist")
    backup = connect(backup_path)
    try:
        version = int(backup.execute("PRAGMA user_version").fetchone()[0])
        required = {"categories", "task_series", "task_occurrences", "reminder_deliveries", "settings"}
        tables = {row[0] for row in backup.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )}
        if version != CURRENT_SCHEMA_VERSION or not required.issubset(tables) or not integrity_check(backup):
            raise BackupError("backup is incompatible or corrupt")
    except sqlite3.DatabaseError as exc:
        raise BackupError("backup is not a valid SQLite database") from exc
    finally:
        backup.close()


def restore_database(source: str | Path, destination: str | Path, pre_restore: str | Path) -> None:
    validate_backup(source)
    current = connect(destination)
    try:
        backup_database(current, pre_restore)
    finally:
        current.close()
    replacement = connect(source)
    target = connect(destination)
    try:
        replacement.backup(target)
    finally:
        replacement.close()
        target.close()
