from datetime import datetime
from pathlib import Path

from mychecklist.app import initialize_database
from mychecklist.config import get_app_paths
from mychecklist.database.migrations import CURRENT_SCHEMA_VERSION
from mychecklist.resources import resource_path


def test_initialize_database_creates_appdata_schema_without_source_files(tmp_path: Path) -> None:
    paths = get_app_paths(tmp_path / "profile with spaces" / "বাংলা")
    connection = initialize_database(paths)
    try:
        assert paths.database.is_file()
        assert paths.database.parent == paths.root
        assert connection.execute("PRAGMA user_version").fetchone()[0] == CURRENT_SCHEMA_VERSION
        assert connection.execute("SELECT COUNT(*) FROM categories").fetchone()[0] == 6
        assert connection.execute(
            "SELECT value FROM settings WHERE key='theme'"
        ).fetchone()[0] == "dark"
        assert not (Path.cwd() / "checklist.db").exists()
    finally:
        connection.close()


def test_resource_path_is_package_relative_and_does_not_use_appdata(tmp_path: Path) -> None:
    resolved = resource_path("theme.py")
    assert resolved.name == "theme.py"
    assert resolved.parent.name == "mychecklist"
    assert tmp_path not in resolved.parents


def test_initialize_database_preserves_existing_data(tmp_path: Path) -> None:
    paths = get_app_paths(tmp_path)
    first = initialize_database(paths)
    first.execute(
        "INSERT INTO settings(key, value, updated_at) VALUES (?, ?, ?)",
        ("custom", "kept", "2026-10-27T00:00:00Z"),
    )
    first.commit()
    first.close()

    second = initialize_database(paths)
    try:
        assert second.execute("SELECT value FROM settings WHERE key='custom'").fetchone()[0] == "kept"
    finally:
        second.close()
