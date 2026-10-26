"""Route-handler composition for the persistent main-window shell."""

from __future__ import annotations

from collections.abc import Callable
from datetime import date, datetime
from pathlib import Path
from typing import Any

from mychecklist.repositories.settings_repository import SettingsRepository
from mychecklist.ui.views.settings import SettingsView
from mychecklist.ui.views.statistics import StatisticsView
from mychecklist.ui.views.task_list import build_task_route_handlers


def build_phase3_route_handlers(
    *,
    ctk_module: Any,
    repository: Any,
    task_service: Any,
    connection: Any,
    database_path: Path,
    category_names: dict[int, str],
    settings: SettingsRepository,
    backup_directory: Path,
    today: Callable[[], date],
    now: Callable[[], datetime] | None,
    on_edit: Callable[[Any], None],
    confirm_delete: Callable[[], bool],
    on_error: Callable[[str], None],
    choose_restore_file: Callable[[], Path | None] | None = None,
    confirm_restore: Callable[[], bool] | None = None,
) -> dict[str, Callable[[Any], None]]:
    handlers = build_task_route_handlers(
        ctk_module=ctk_module, repository=repository, task_service=task_service,
        category_names=category_names, today=today, now=now, on_edit=on_edit,
        confirm_delete=confirm_delete, on_error=on_error,
    )

    def render_statistics(parent: Any) -> None:
        StatisticsView(parent, ctk_module, connection=connection, today=today, on_error=on_error)

    def render_settings(parent: Any) -> None:
        SettingsView(
            parent, ctk_module, settings=settings, connection=connection,
            database_path=database_path,
            backup_directory=backup_directory, on_error=on_error,
            choose_restore_file=choose_restore_file, confirm_restore=confirm_restore,
        )

    handlers["statistics"] = render_statistics
    handlers["settings"] = render_settings
    return handlers
