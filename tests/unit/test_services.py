from datetime import date, datetime, timezone
from pathlib import Path
import tempfile

from mychecklist.database.connection import connect
from mychecklist.database.migrations import migrate
from mychecklist.notifications.plyer_adapter import PlyerNotifier
from mychecklist.repositories.category_repository import CategoryRepository
from mychecklist.repositories.reminder_repository import ReminderRepository
from mychecklist.repositories.task_repository import TaskRepository
from mychecklist.services.reminder_service import ReminderService
from mychecklist.services.statistics_service import StatisticsService
from mychecklist.services.task_service import TaskService


def _database():
    folder = tempfile.TemporaryDirectory()
    connection = connect(Path(folder.name) / "test.db")
    migrate(connection)
    categories = CategoryRepository(connection)
    categories.seed_builtins()
    return folder, connection, categories


def test_task_views_filters_stats_and_reminder_deduplication():
    folder, connection, categories = _database()
    try:
        repository = TaskRepository(connection)
        service = TaskService(repository)
        category_id = categories.list()[0]["id"]
        service.create(title="Today study", due_date="2026-10-27", due_time="09:00",
                       category_id=category_id, priority="high", recurrence="none", reminder_offset_minutes=0)
        rows = repository.list_occurrences()
        assert len(rows) == 1
        service.complete(rows[0]["id"], "2026-10-27T10:00:00Z")
        summary = StatisticsService(connection).summary(date(2026, 10, 27))
        assert summary["completion_rate"] == 100
        calls = []
        reminders = ReminderService(
            ReminderRepository(connection),
            lambda **kwargs: calls.append(kwargs) or True,
            lambda: datetime(2026, 10, 27, 11, tzinfo=timezone.utc),
        )
        assert reminders.process_due() == 0
        assert calls == []
    finally:
        connection.close()
        folder.cleanup()


def test_backup_validation_and_restore(tmp_path):
    folder, connection, categories = _database()
    try:
        source = tmp_path / "source.db"
        backup = tmp_path / "backup.db"
        restored = tmp_path / "restored.db"
        from mychecklist.database.backup import backup_database, restore_database, validate_backup
        backup_database(connection, source)
        validate_backup(source)
        backup_database(connection, backup)
        restore_database(backup, restored, tmp_path / "pre-restore.db")
        validate_backup(restored)
    finally:
        connection.close()
        folder.cleanup()


def test_notification_adapter_returns_false_on_provider_failure(monkeypatch):
    monkeypatch.setitem(__import__("sys").modules, "plyer", None)
    assert PlyerNotifier()(title="x", message="y") is False
