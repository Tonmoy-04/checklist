from datetime import date
import sqlite3

from mychecklist.database.connection import connect
from mychecklist.database.migrations import CURRENT_SCHEMA_VERSION, integrity_check, migrate
from mychecklist.repositories.category_repository import CategoryRepository
from mychecklist.repositories.task_repository import TaskRepository
from mychecklist.services.recurrence_service import next_occurrence_date


def test_schema_seed_constraints_and_recurring_completion(tmp_path):
    connection = connect(tmp_path / "test.db")
    migrate(connection)
    assert connection.execute("PRAGMA foreign_keys").fetchone()[0] == 1
    assert connection.execute("PRAGMA user_version").fetchone()[0] == CURRENT_SCHEMA_VERSION
    assert integrity_check(connection)
    categories = CategoryRepository(connection)
    categories.seed_builtins()
    categories.seed_builtins()
    assert len(categories.list()) == 6
    tasks = TaskRepository(connection)
    category_id = categories.list()[0]["id"]
    occurrence_id = tasks.create_series("Monthly", category_id, "high", "monthly", date(2024, 1, 31))
    tasks.complete_occurrence(occurrence_id, "2024-01-31T00:00:00Z")
    rows = tasks.list_occurrences()
    assert len(rows) == 2
    assert rows[1]["due_date"] == "2024-02-29"
    tasks.complete_occurrence(occurrence_id, "2024-01-31T00:00:00Z")
    assert len(tasks.list_occurrences()) == 2
    connection.close()


def test_foreign_keys_and_duplicate_occurrences(tmp_path):
    connection = connect(tmp_path / "test.db")
    migrate(connection)
    categories = CategoryRepository(connection)
    categories.seed_builtins()
    tasks = TaskRepository(connection)
    category_id = categories.list()[0]["id"]
    series_id = tasks.create_series("Task", category_id, "low", "none", date.today())
    try:
        tasks.add_occurrence(series_id, date.today())
    except sqlite3.IntegrityError:
        pass
    else:
        raise AssertionError("duplicate occurrence was accepted")
    assert next_occurrence_date(date(2025, 1, 31), "monthly") == date(2025, 2, 28)
    connection.close()
