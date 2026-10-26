from datetime import date, datetime, timezone
import sqlite3

import pytest

from mychecklist.database.backup import BackupError, backup_database, validate_backup
from mychecklist.database.connection import connect
from mychecklist.database.migrations import CURRENT_SCHEMA_VERSION, migrate
from mychecklist.repositories.category_repository import CategoryRepository
from mychecklist.repositories.reminder_repository import ReminderRepository
from mychecklist.repositories.task_repository import TaskRepository
from mychecklist.services.recurrence_service import next_occurrence_date
from mychecklist.services.reminder_service import ReminderService
from mychecklist.services.task_service import TaskService
from mychecklist.services.validation import ValidationError, validate_task_input


def _db(path):
    connection = connect(path)
    migrate(connection)
    categories = CategoryRepository(connection)
    categories.seed_builtins()
    return connection, categories.list()[0]["id"]


def _valid_task(title):
    return dict(
        title=title, due_date="2026-10-27", due_time=None, category_id=1,
        priority="medium", recurrence="none", reminder_offset_minutes=None,
    )


@pytest.mark.parametrize("title", ["", " ", "\t\n"])
def test_title_rejects_empty_and_whitespace(title):
    with pytest.raises(ValidationError):
        validate_task_input(**_valid_task(title))


def test_title_boundaries_unicode_and_service_create_update(tmp_path):
    connection, category_id = _db(tmp_path / "titles.db")
    try:
        service = TaskService(TaskRepository(connection))
        minimum = service.create(**_valid_task("x") | {"category_id": category_id})
        assert minimum > 0
        maximum_title = "বাংলা " + ("ü" * 194)
        assert len(maximum_title) == 200
        normalized = validate_task_input(**_valid_task(f"  {maximum_title}  ") | {"category_id": category_id})
        assert normalized.title == maximum_title
        series_id = service.create(**_valid_task(f"  {maximum_title}  ") | {"category_id": category_id})
        with pytest.raises(ValidationError):
            service.create(**_valid_task("x" * 201) | {"category_id": category_id})
        with pytest.raises(ValidationError):
            validate_task_input(**_valid_task("x" * 201) | {"category_id": category_id})
        service.update(series_id, **_valid_task("  إصلاح  ") | {"category_id": category_id})
        assert connection.execute("SELECT title FROM task_series WHERE id=?", (series_id,)).fetchone()[0] == "إصلاح"
    finally:
        connection.close()


def test_date_time_boundaries_leap_day_and_past_date(tmp_path):
    connection, category_id = _db(tmp_path / "dates.db")
    try:
        service = TaskService(TaskRepository(connection))
        assert service.create(**_valid_task("Past") | {
            "category_id": category_id, "due_date": "2024-02-29", "due_time": "00:00"
        })
        with pytest.raises(ValidationError):
            service.create(**_valid_task("Bad date") | {"category_id": category_id, "due_date": "2025-02-29"})
        with pytest.raises(ValidationError):
            service.create(**_valid_task("Bad time") | {"category_id": category_id, "due_time": "24:00"})
    finally:
        connection.close()


def test_monthly_recurrence_boundaries_and_year_rollover():
    assert next_occurrence_date(date(2024, 1, 31), "monthly") == date(2024, 2, 29)
    assert next_occurrence_date(date(2025, 1, 31), "monthly") == date(2025, 2, 28)
    assert next_occurrence_date(date(2024, 12, 31), "monthly") == date(2025, 1, 31)
    assert next_occurrence_date(date(2024, 1, 30), "monthly", 12) == date(2025, 1, 30)


def test_completion_is_idempotent_and_reopen_preserves_next_occurrence(tmp_path):
    connection, category_id = _db(tmp_path / "recurrence.db")
    try:
        repository = TaskRepository(connection)
        service = TaskService(repository)
        series_id = service.create(**_valid_task("Daily") | {
            "category_id": category_id, "recurrence": "daily"
        })
        occurrence_id = repository.list_occurrences()[0]["id"]
        service.complete(occurrence_id, "2026-10-27T00:00:00Z")
        service.complete(occurrence_id, "2026-10-27T00:00:00Z")
        assert len(repository.list_occurrences()) == 2
        service.reopen(occurrence_id)
        assert len(repository.list_occurrences()) == 2
        assert repository.get_occurrence(occurrence_id)["status"] == "open"
        service.cancel_occurrence(repository.list_occurrences()[1]["id"])
        assert len(repository.list_occurrences()) == 2
        service.delete_series(series_id)
        assert all(row["status"] != "open" for row in repository.list_occurrences())
    finally:
        connection.close()


def test_reminder_missed_policy_and_failure_retry_bound(tmp_path):
    connection, category_id = _db(tmp_path / "reminders.db")
    try:
        repository = TaskRepository(connection)
        service = TaskService(repository)
        service.create(**_valid_task("Reminder") | {
            "category_id": category_id, "due_date": "2026-10-26", "due_time": "09:00"
        })
        notifier_calls = []
        clock = lambda: datetime(2026, 10, 27, 9, tzinfo=timezone.utc)
        no_missed = ReminderService(
            ReminderRepository(connection), lambda **kwargs: notifier_calls.append(kwargs) or True,
            clock, notify_missed_reminders=False,
        )
        assert no_missed.process_due() == 0
        failing = ReminderService(
            ReminderRepository(connection), lambda **kwargs: False,
            clock, notify_missed_reminders=True,
        )
        assert failing.process_due() == 1
        assert failing.process_due() == 1
        assert failing.process_due() == 1
        assert failing.process_due() == 0
    finally:
        connection.close()


def test_backup_rejects_corrupt_and_incompatible_files(tmp_path):
    connection, _ = _db(tmp_path / "source.db")
    try:
        backup = tmp_path / "backup.db"
        backup_database(connection, backup)
        validate_backup(backup)
        corrupt = tmp_path / "corrupt.db"
        corrupt.write_bytes(b"not sqlite")
        with pytest.raises(BackupError):
            validate_backup(corrupt)
        incompatible = tmp_path / "incompatible.db"
        other = sqlite3.connect(incompatible)
        other.execute(f"PRAGMA user_version = {CURRENT_SCHEMA_VERSION + 1}")
        other.commit()
        other.close()
        with pytest.raises(BackupError):
            validate_backup(incompatible)
    finally:
        connection.close()


def test_missing_app_data_and_locked_database_are_explicit(tmp_path, monkeypatch):
    from mychecklist.config import ConfigurationError, get_app_paths
    monkeypatch.delenv("LOCALAPPDATA", raising=False)
    with pytest.raises(ConfigurationError):
        get_app_paths()
    database = tmp_path / "locked.db"
    first = connect(database)
    migrate(first)
    try:
        second = connect(database, timeout=0.01)
        try:
            first.execute("BEGIN EXCLUSIVE")
            with pytest.raises(sqlite3.OperationalError):
                second.execute("CREATE TABLE locked_probe (id INTEGER)").fetchone()
        finally:
            second.close()
    finally:
        first.rollback()
        first.close()


def test_unsupported_migration_version_does_not_modify_database(tmp_path):
    database = tmp_path / "migration.db"
    connection = connect(database)
    try:
        connection.execute(f"PRAGMA user_version = {CURRENT_SCHEMA_VERSION + 1}")
        connection.commit()
        with pytest.raises(RuntimeError, match="Unsupported database schema version"):
            migrate(connection)
        assert connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='task_series'"
        ).fetchone() is None
        assert connection.execute("PRAGMA user_version").fetchone()[0] == CURRENT_SCHEMA_VERSION + 1
    finally:
        connection.close()
