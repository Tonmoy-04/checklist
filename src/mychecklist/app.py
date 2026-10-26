"""Application composition root for development and packaged launches."""

from __future__ import annotations

import logging
from collections.abc import Callable
from datetime import date, datetime
from pathlib import Path
from typing import Any

from mychecklist.config import AppPaths, get_app_paths
from mychecklist.database.connection import connect
from mychecklist.database.migrations import integrity_check, migrate
from mychecklist.logging_config import configure_logging
from mychecklist.notifications.plyer_adapter import PlyerNotifier
from mychecklist.repositories.category_repository import CategoryRepository
from mychecklist.repositories.reminder_repository import ReminderRepository
from mychecklist.repositories.settings_repository import SettingsRepository
from mychecklist.repositories.task_repository import TaskRepository
from mychecklist.services.reminder_poller import ReminderPoller
from mychecklist.services.reminder_service import ReminderService
from mychecklist.services.task_service import TaskService
from mychecklist.theme import configure_customtkinter
from mychecklist.ui.main_window import MainWindow
from mychecklist.ui.views.routes import build_phase3_route_handlers

logger = logging.getLogger(__name__)


def initialize_database(paths: AppPaths) -> Any:
    """Create/open the production database and apply its migrations."""
    paths.ensure_directories()
    connection = connect(paths.database)
    try:
        migrate(connection)
        if not integrity_check(connection):
            raise RuntimeError("SQLite integrity check failed after migration")
        CategoryRepository(connection).seed_builtins()
        SettingsRepository(connection).seed_defaults()
        return connection
    except Exception:
        connection.close()
        raise


class Application:
    """Own long-lived database, scheduler, and window resources."""

    def __init__(
        self,
        root: Any,
        ctk_module: Any,
        *,
        paths: AppPaths,
        connection: Any,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self.root = root
        self.ctk = ctk_module
        self.paths = paths
        self.connection = connection
        self.settings = SettingsRepository(connection)
        self.task_repository = TaskRepository(connection)
        self.task_service = TaskService(self.task_repository)
        categories = CategoryRepository(connection).list()
        category_names = {row["id"]: row["name"] for row in categories}
        reminder_service = ReminderService(
            ReminderRepository(connection),
            PlyerNotifier(),
            clock=clock,
            notify_missed_reminders=self.settings.get("notify_missed_reminders", "true") == "true",
        )
        self.poller = ReminderPoller(
            root,
            lambda: reminder_service.process_due(
                int(self.settings.get("default_reminder_offset_minutes", "0") or 0)
            ),
            on_error=self._show_error,
        )
        self.window = MainWindow(
            root,
            ctk_module,
            route_handlers=build_phase3_route_handlers(
                ctk_module=ctk_module,
                repository=self.task_repository,
                task_service=self.task_service,
                connection=connection,
                database_path=paths.database,
                category_names=category_names,
                settings=self.settings,
                backup_directory=paths.backups,
                today=(lambda: (clock() if clock else datetime.now()).date()),
                now=clock,
                on_edit=self._edit_task,
                on_add_task=self._add_task,
                confirm_delete=self._confirm_delete,
                on_error=self._show_error,
            ),
            reminder_poller=self.poller,
            on_close=self.close,
        )
        self._closed = False

    def _add_task(self, refresh: Callable[[], None]) -> None:
        from mychecklist.ui.dialogs.task_editor import TaskEditorDialog

        categories = {
            category["id"]: category["name"]
            for category in CategoryRepository(self.connection).list()
        }
        initial = {"category_id": next(iter(categories), None)}
        TaskEditorDialog(
            self.root,
            self.ctk,
            categories=categories,
            initial=initial,
            on_save=lambda values: (self.task_service.create_validated(values), refresh()),
            show_error=self._show_error,
        )

    def _edit_task(self, row: Any) -> None:
        from mychecklist.ui.dialogs.task_editor import TaskEditorDialog

        TaskEditorDialog(
            self.root,
            self.ctk,
            categories={
                category["id"]: category["name"]
                for category in CategoryRepository(self.connection).list()
            },
            initial=dict(row),
            on_save=lambda values: self.task_service.update_validated(row["series_id"], values),
            show_error=self._show_error,
        )

    def _confirm_delete(self) -> bool:
        from tkinter import messagebox

        return bool(messagebox.askyesno("Delete task?", "Cancel this task occurrence?", parent=self.root))

    def _show_error(self, message: str) -> None:
        logger.error("%s", message)

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        self.connection.close()


def create_application(
    *,
    local_app_data: str | Path | None = None,
    ctk_module: Any | None = None,
    root: Any | None = None,
    clock: Callable[[], datetime] | None = None,
) -> Application:
    """Build the application without entering the GUI event loop."""
    paths = get_app_paths(local_app_data)
    configure_logging(paths.logs)
    ctk = configure_customtkinter(ctk_module)
    window_root = root or ctk.CTk()
    connection = initialize_database(paths)
    try:
        return Application(window_root, ctk, paths=paths, connection=connection, clock=clock)
    except Exception:
        connection.close()
        if root is None and hasattr(window_root, "destroy"):
            window_root.destroy()
        raise


def run() -> None:
    """Launch the GUI and report startup failures through logging."""
    try:
        application = create_application()
        application.root.mainloop()
    except Exception:
        logger.exception("MyChecklist failed to start")
        raise
