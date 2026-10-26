from __future__ import annotations

import sqlite3
from datetime import date, datetime, timezone

from mychecklist.services.recurrence_service import next_occurrence_date


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class TaskRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def create_series(self, title: str, category_id: int, priority: str, recurrence: str,
                      start_date: date, due_time: str | None = None, interval_count: int = 1) -> int:
        title = title.strip()
        if not 1 <= len(title) <= 200:
            raise ValueError("title must be 1-200 characters")
        if priority not in {"low", "medium", "high"} or recurrence not in {"none", "daily", "weekly", "monthly"}:
            raise ValueError("invalid priority or recurrence")
        stamp = _now()
        with self.connection:
            cursor = self.connection.execute(
                """INSERT INTO task_series
                   (title, category_id, priority, recurrence, interval_count, start_date, due_time, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (title, category_id, priority, recurrence, interval_count, start_date.isoformat(), due_time, stamp, stamp),
            )
            series_id = int(cursor.lastrowid)
            self.add_occurrence(series_id, start_date, due_time)
        return series_id

    def add_occurrence(self, series_id: int, due_date: date, due_time: str | None = None) -> int:
        stamp = _now()
        cursor = self.connection.execute(
            """INSERT INTO task_occurrences
               (series_id, due_date, due_time, due_time_key, status, created_at, updated_at)
               VALUES (?, ?, ?, ?, 'open', ?, ?)""",
            (series_id, due_date.isoformat(), due_time, due_time or "", stamp, stamp),
        )
        return int(cursor.lastrowid)

    def get_occurrence(self, occurrence_id: int) -> sqlite3.Row | None:
        return self.connection.execute("SELECT * FROM task_occurrences WHERE id = ?", (occurrence_id,)).fetchone()

    def list_occurrences(self, status: str | None = None) -> list[sqlite3.Row]:
        query = (
            "SELECT o.*, s.title, s.category_id, s.priority, s.recurrence, s.is_active AS series_is_active "
            "FROM task_occurrences o JOIN task_series s ON s.id=o.series_id"
        )
        parameters: tuple[object, ...] = ()
        if status is not None:
            query += " WHERE o.status=?"
            parameters = (status,)
        query += " ORDER BY o.due_date, o.due_time, o.id"
        return list(self.connection.execute(query, parameters))

    def update_series(self, series_id: int, *, title: str, category_id: int, priority: str,
                      recurrence: str, start_date: date, due_time: str | None = None,
                      interval_count: int = 1) -> None:
        title = title.strip()
        if not 1 <= len(title) <= 200:
            raise ValueError("title must be 1-200 characters")
        stamp = _now()
        with self.connection:
            cursor = self.connection.execute(
                """UPDATE task_series SET title=?, category_id=?, priority=?, recurrence=?,
                   start_date=?, due_time=?, interval_count=?, updated_at=? WHERE id=?""",
                (title, category_id, priority, recurrence, start_date.isoformat(), due_time,
                 interval_count, stamp, series_id),
            )
            if cursor.rowcount != 1:
                raise KeyError(series_id)

    def complete_occurrence(self, occurrence_id: int, completed_at: str | None = None) -> None:
        stamp = completed_at or _now()
        with self.connection:
            occurrence = self.get_occurrence(occurrence_id)
            if occurrence is None:
                raise KeyError(occurrence_id)
            if occurrence["status"] == "completed":
                return
            self.connection.execute(
                "UPDATE task_occurrences SET status='completed', completed_at=?, updated_at=? WHERE id=?",
                (stamp, stamp, occurrence_id),
            )
            series = self.connection.execute("SELECT * FROM task_series WHERE id=?", (occurrence["series_id"],)).fetchone()
            if series["is_active"] and series["recurrence"] != "none":
                next_date = next_occurrence_date(date.fromisoformat(occurrence["due_date"]),
                                                  series["recurrence"], series["interval_count"])
                self.connection.execute(
                    """INSERT OR IGNORE INTO task_occurrences
                       (series_id, due_date, due_time, due_time_key, status, created_at, updated_at)
                       VALUES (?, ?, ?, ?, 'open', ?, ?)""",
                    (series["id"], next_date.isoformat(), series["due_time"], series["due_time"] or "", stamp, stamp),
                )

    def reopen_occurrence(self, occurrence_id: int) -> None:
        with self.connection:
            if self.get_occurrence(occurrence_id) is None:
                raise KeyError(occurrence_id)
            self.connection.execute(
                "UPDATE task_occurrences SET status='open', completed_at=NULL, updated_at=? WHERE id=?",
                (_now(), occurrence_id),
            )

    def cancel_occurrence(self, occurrence_id: int) -> None:
        with self.connection:
            self.connection.execute(
                "UPDATE task_occurrences SET status='cancelled', completed_at=NULL, updated_at=? WHERE id=?",
                (_now(), occurrence_id),
            )

    def stop_series(self, series_id: int) -> None:
        with self.connection:
            self.connection.execute("UPDATE task_series SET is_active=0, updated_at=? WHERE id=?", (_now(), series_id))
            self.connection.execute(
                "UPDATE task_occurrences SET status='cancelled', updated_at=? WHERE series_id=? AND status='open'",
                (_now(), series_id),
            )

    def delete_series(self, series_id: int) -> None:
        self.stop_series(series_id)
