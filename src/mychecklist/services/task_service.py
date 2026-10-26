"""Task use cases independent of the graphical interface."""
from __future__ import annotations

from datetime import date, datetime
from typing import Any

from mychecklist.repositories.task_repository import TaskRepository
from mychecklist.services.validation import ValidatedTaskInput, validate_task_input


class TaskService:
    def __init__(self, repository: TaskRepository) -> None:
        self.repository = repository

    def create(self, **fields: Any) -> int:
        values = self._validate(fields)
        return self.create_validated(values)

    def create_validated(self, values: ValidatedTaskInput) -> int:
        self._require_category(values.category_id)
        return self.repository.create_series(
            values.title, values.category_id, values.priority, values.recurrence,
            values.due_date, values.due_time,
        )

    def update(self, series_id: int, **fields: Any) -> None:
        values = self._validate(fields)
        self.update_validated(series_id, values)

    def update_validated(self, series_id: int, values: ValidatedTaskInput) -> None:
        self._require_category(values.category_id)
        self.repository.update_series(
            series_id, title=values.title, category_id=values.category_id,
            priority=values.priority, recurrence=values.recurrence,
            start_date=values.due_date, due_time=values.due_time,
        )

    def complete(self, occurrence_id: int, completed_at: str | None = None) -> None:
        self.repository.complete_occurrence(occurrence_id, completed_at)

    def reopen(self, occurrence_id: int) -> None:
        self.repository.reopen_occurrence(occurrence_id)

    def cancel_occurrence(self, occurrence_id: int) -> None:
        self.repository.cancel_occurrence(occurrence_id)

    def delete_series(self, series_id: int) -> None:
        self.repository.stop_series(series_id)

    def _validate(self, fields: dict[str, Any]) -> ValidatedTaskInput:
        return validate_task_input(
            title=fields.get("title", ""),
            due_date=fields.get("due_date", ""),
            due_time=fields.get("due_time"),
            category_id=fields.get("category_id"),
            priority=fields.get("priority", ""),
            recurrence=fields.get("recurrence", ""),
            reminder_offset_minutes=fields.get("reminder_offset_minutes"),
        )

    def _require_category(self, category_id: int) -> None:
        row = self.repository.connection.execute(
            "SELECT id FROM categories WHERE id = ? AND is_archived = 0", (category_id,)
        ).fetchone()
        if row is None:
            raise ValueError("category does not exist or is archived")


def _due_datetime(row: Any) -> datetime:
    return datetime.fromisoformat(f"{row['due_date']}T{row['due_time'] or '23:59'}")


def query_view(repository: TaskRepository, view: str, today: date,
               now: datetime | None = None) -> list[Any]:
    """Return active occurrence rows for a documented navigation view."""
    if hasattr(repository, "list_for_view"):
        return repository.list_for_view(view, today, now)
    rows = repository.list_occurrences()
    active = [row for row in rows if row["status"] == "open" and row["series_is_active"]]
    if view == "today":
        return [row for row in active if row["due_date"] == today.isoformat()]
    if view == "upcoming":
        return [row for row in active if row["due_date"] > today.isoformat()]
    if view == "overdue":
        current = now or datetime.now()
        return [row for row in active if _due_datetime(row) < current]
    if view == "all":
        return active
    if view == "completed":
        return [row for row in rows if row["status"] == "completed"]
    raise ValueError(f"unsupported view: {view}")


def filter_and_sort(rows: list[Any], *, search: str = "", category_id: int | None = None,
                    priority: str | None = None, sort_by: str = "due") -> list[Any]:
    needle = search.strip().casefold()
    filtered = [
        row for row in rows
        if (not needle or needle in row["title"].casefold())
        and (category_id is None or row["category_id"] == category_id)
        and (priority is None or row["priority"] == priority)
    ]
    if sort_by == "priority":
        order = {"high": 0, "medium": 1, "low": 2}
        return sorted(filtered, key=lambda row: (order[row["priority"]], row["due_date"], row["id"]))
    if sort_by == "created":
        return sorted(filtered, key=lambda row: (row["created_at"], row["id"]), reverse=True)
    if sort_by != "due":
        raise ValueError(f"unsupported sort: {sort_by}")
    return sorted(filtered, key=lambda row: (row["due_date"], row["due_time"] or "23:59", row["id"]))
