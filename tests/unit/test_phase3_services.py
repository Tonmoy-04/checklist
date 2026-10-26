from datetime import date

from mychecklist.repositories.settings_repository import SettingsRepository
from mychecklist.services.reminder_poller import ReminderPoller
from mychecklist.services.task_service import filter_and_sort
from mychecklist.services.statistics_service import StatisticsService
from mychecklist.database.connection import connect
from mychecklist.database.migrations import migrate


def _row(identifier, title, priority, due_date, created_at, category_id=1):
    return {
        "id": identifier, "title": title, "priority": priority,
        "due_date": due_date, "due_time": None, "created_at": created_at,
        "category_id": category_id,
    }


def test_filter_and_sort_search_filters_and_clear_are_non_mutating():
    rows = [
        _row(1, "Read notes", "low", "2026-10-28", "2026-10-27T01:00:00Z"),
        _row(2, "Submit report", "high", "2026-10-27", "2026-10-27T02:00:00Z"),
    ]
    assert [row["id"] for row in filter_and_sort(rows, search="REPORT")] == [2]
    assert [row["id"] for row in filter_and_sort(rows, priority="high")] == [2]
    assert [row["id"] for row in filter_and_sort(rows, sort_by="priority")] == [2, 1]
    assert [row["id"] for row in filter_and_sort(rows, sort_by="created")] == [2, 1]
    assert [row["id"] for row in rows] == [1, 2]
    assert filter_and_sort(rows, search="missing") == []


def test_statistics_empty_summary_is_zero_safe(tmp_path):
    connection = connect(tmp_path / "empty.db")
    try:
        migrate(connection)
        summary = StatisticsService(connection).summary(date(2026, 10, 27))
        assert summary["due_today"] == 0
        assert summary["completion_rate"] == 0
        assert summary["category_breakdown"] == {}
    finally:
        connection.close()


def test_settings_repository_round_trips_values(tmp_path):
    connection = connect(tmp_path / "settings.db")
    try:
        migrate(connection)
        repository = SettingsRepository(connection)
        repository.set("theme", "light")
        assert repository.get("theme") == "light"
        assert repository.get("missing", "fallback") == "fallback"
    finally:
        connection.close()


def test_reminder_poller_uses_scheduler_and_stops():
    class Scheduler:
        def __init__(self):
            self.callback = None
            self.cancelled = []
        def after(self, interval, callback):
            self.callback = callback
            return "timer"
        def after_cancel(self, timer):
            self.cancelled.append(timer)

    scheduler = Scheduler()
    calls = []
    poller = ReminderPoller(scheduler, lambda: calls.append(True), interval_ms=5)
    poller.start()
    scheduler.callback()
    assert calls == [True]
    poller.stop()
    assert scheduler.cancelled == ["timer"]
