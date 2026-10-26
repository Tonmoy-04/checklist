from pathlib import Path

import pytest

from mychecklist.config import ConfigurationError, get_app_paths


def test_get_app_paths_uses_local_app_data_without_creating_files(tmp_path: Path) -> None:
    paths = get_app_paths(tmp_path)

    assert paths.root == tmp_path / "MyChecklist"
    assert paths.database == paths.root / "checklist.db"
    assert paths.backups == paths.root / "backups"
    assert paths.logs == paths.root / "logs"
    assert not paths.root.exists()


def test_get_app_paths_requires_local_app_data(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("LOCALAPPDATA", raising=False)

    with pytest.raises(ConfigurationError):
        get_app_paths()


def test_ensure_directories_creates_only_app_data_directories(tmp_path: Path) -> None:
    paths = get_app_paths(tmp_path)

    paths.ensure_directories()

    assert paths.root.is_dir()
    assert paths.backups.is_dir()
    assert paths.logs.is_dir()
    assert not (Path.cwd() / "checklist.db").exists()
