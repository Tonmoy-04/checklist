"""SQLite connection factory."""
from __future__ import annotations

import sqlite3
from pathlib import Path


def connect(database: str | Path, *, timeout: float = 5.0) -> sqlite3.Connection:
    path = str(database)
    if path != ":memory:":
        Path(path).parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, timeout=timeout)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute(f"PRAGMA busy_timeout = {int(timeout * 1000)}")
    return connection
