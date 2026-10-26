"""Application paths and configuration helpers."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


class ConfigurationError(RuntimeError):
    """Raised when the required Windows application-data location is unavailable."""


@dataclass(frozen=True)
class AppPaths:
    """Locations for mutable MyChecklist application data."""

    root: Path

    @property
    def database(self) -> Path:
        return self.root / "checklist.db"

    @property
    def backups(self) -> Path:
        return self.root / "backups"

    @property
    def logs(self) -> Path:
        return self.root / "logs"

    def ensure_directories(self) -> None:
        """Create the application-data directories when the app starts."""
        self.root.mkdir(parents=True, exist_ok=True)
        self.backups.mkdir(parents=True, exist_ok=True)
        self.logs.mkdir(parents=True, exist_ok=True)


def get_app_paths(local_app_data: str | os.PathLike[str] | None = None) -> AppPaths:
    """Resolve MyChecklist paths under ``%LOCALAPPDATA%``.

    The optional argument exists for deterministic tests and dependency injection.
    This function does not create directories or files.
    """
    base = Path(local_app_data) if local_app_data is not None else _local_app_data_from_environment()
    return AppPaths(root=base / "MyChecklist")


def _local_app_data_from_environment() -> Path:
    value = os.environ.get("LOCALAPPDATA")
    if not value:
        raise ConfigurationError("LOCALAPPDATA is not set; cannot determine the MyChecklist data directory.")
    return Path(value)
