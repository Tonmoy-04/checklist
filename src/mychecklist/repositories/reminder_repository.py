from __future__ import annotations

import sqlite3
from datetime import datetime, timezone


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class ReminderRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def claim_due(
        self, now: str, offset: int, *, notify_missed: bool = True, max_attempts: int = 3
    ) -> list[sqlite3.Row]:
        with self.connection:
            rows = list(self.connection.execute(
                """SELECT o.id, s.title, o.due_date, o.due_time
                   FROM task_occurrences o JOIN task_series s ON s.id=o.series_id
                   WHERE o.status='open'
                     AND datetime(o.due_date || ' ' || COALESCE(o.due_time, '23:59'),
                                  '-' || ? || ' minutes') <= datetime(?)
                   AND (? OR datetime(o.due_date || ' ' || COALESCE(o.due_time, '23:59')) >= datetime(?))
                   AND NOT EXISTS (
                     SELECT 1 FROM reminder_deliveries d
                     WHERE d.occurrence_id=o.id AND d.reminder_offset_minutes=?
                       AND (d.status IN ('pending', 'delivered')
                            OR (d.status='failed' AND d.attempt_count >= ?))
                   )""",
                (offset, now, int(notify_missed), now, offset, max_attempts),
            ))
            for row in rows:
                self.connection.execute(
                    """INSERT OR IGNORE INTO reminder_deliveries
                       (occurrence_id, reminder_offset_minutes, scheduled_for, status, created_at)
                       VALUES (?, ?, ?, 'pending', ?)""",
                    (row["id"], offset, now, _now()),
                )
            return rows

    def record(self, occurrence_id: int, offset: int, *, delivered: bool, error_code: str | None = None) -> None:
        stamp = _now()
        with self.connection:
            self.connection.execute(
                """UPDATE reminder_deliveries
                   SET attempted_at=?, delivered_at=?, status=?, attempt_count=attempt_count+1, last_error_code=?
                   WHERE occurrence_id=? AND reminder_offset_minutes=?""",
                (stamp, stamp if delivered else None, "delivered" if delivered else "failed",
                 error_code, occurrence_id, offset),
            )
