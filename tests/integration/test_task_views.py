from datetime import date, datetime
from pathlib import Path

from mychecklist.database.connection import connect
from mychecklist.database.migrations import migrate
from mychecklist.repositories.category_repository import CategoryRepository
from mychecklist.repositories.task_repository import TaskRepository
from mychecklist.services.task_service import TaskService, query_view


def test_task_views_apply_date_status_and_cancellation_rules(tmp_path: Path) -> None:
    connection = connect(tmp_path / "views.db")
    try:
        migrate(connection)
        categories = CategoryRepository(connection)
        categories.seed_builtins()
        category_id = categories.list()[0]["id"]
        service = TaskService(TaskRepository(connection))
        service.create(title="Today", due_date="2026-10-27", due_time="09:00",
                       category_id=category_id, priority="high", recurrence="none",
                       reminder_offset_minutes=None)
        service.create(title="All day today", due_date="2026-10-27", due_time=None,
                       category_id=category_id, priority="low", recurrence="none",
                       reminder_offset_minutes=None)
        service.create(title="Future", due_date="2026-10-28", due_time="08:00",
                       category_id=category_id, priority="low", recurrence="none",
                       reminder_offset_minutes=None)
        service.create(title="Past", due_date="2026-10-26", due_time=None,
                       category_id=category_id, priority="medium", recurrence="none",
                       reminder_offset_minutes=None)
        repository = TaskRepository(connection)
        today = date(2026, 10, 27)
        now = datetime(2026, 10, 27, 10, 0)
        assert len(query_view(repository, "today", today, now)) == 2
        assert [row["title"] for row in query_view(repository, "upcoming", today, now)] == ["Future"]
        assert [row["title"] for row in query_view(repository, "overdue", today, now)] == ["Past", "Today"]
        assert len(query_view(repository, "all", today, now)) == 4
        past_id = next(row["id"] for row in repository.list_occurrences() if row["title"] == "Past")
        service.complete(past_id, "2026-10-27T11:00:00Z")
        assert [row["title"] for row in query_view(repository, "completed", today, now)] == ["Past"]
        assert [row["title"] for row in query_view(repository, "overdue", today, now)] == ["Today"]
        service.cancel_occurrence(next(row["id"] for row in repository.list_occurrences() if row["title"] == "Future"))
        assert query_view(repository, "upcoming", today, now) == []
    finally:
        connection.close()
