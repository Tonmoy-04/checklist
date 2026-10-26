"""Persisted occurrence statistics."""
from __future__ import annotations

from datetime import date, timedelta
from typing import Any


class StatisticsService:
    def __init__(self, connection: Any) -> None:
        self.connection = connection

    def summary(self, today: date) -> dict[str, Any]:
        rows = list(self.connection.execute(
            "SELECT due_date, status, completed_at FROM task_occurrences WHERE status != 'cancelled'"
        ))
        due_today = [row for row in rows if row["due_date"] == today.isoformat()]
        completed_today = [row for row in due_today if row["status"] == "completed"]
        denominator = len(due_today)
        return {
            "due_today": denominator,
            "completed_today": len(completed_today),
            "remaining_today": denominator - len(completed_today),
            "completion_rate": (len(completed_today) / denominator * 100) if denominator else 0,
            "completed_last_7_days": self._completed_since(today - timedelta(days=6)),
            "completed_last_30_days": self._completed_since(today - timedelta(days=29)),
            "category_breakdown": self._breakdown("category_id"),
            "priority_breakdown": self._breakdown("priority"),
        }

    def _completed_since(self, start: date) -> int:
        return self.connection.execute(
            "SELECT COUNT(*) FROM task_occurrences WHERE status='completed' AND substr(completed_at, 1, 10) >= ?",
            (start.isoformat(),),
        ).fetchone()[0]

    def _breakdown(self, field: str) -> dict[str, int]:
        if field not in {"category_id", "priority"}:
            raise ValueError(field)
        if field == "priority":
            rows = self.connection.execute(
                "SELECT s.priority AS label, COUNT(*) AS count FROM task_occurrences o "
                "JOIN task_series s ON s.id=o.series_id WHERE o.status='completed' GROUP BY s.priority"
            )
        else:
            rows = self.connection.execute(
                "SELECT c.name AS label, COUNT(*) AS count FROM task_occurrences o "
                "JOIN task_series s ON s.id=o.series_id JOIN categories c ON c.id=s.category_id "
                "WHERE o.status='completed' GROUP BY c.id, c.name"
            )
        return {row["label"]: row["count"] for row in rows}
