"""Task-list screens for the five occurrence navigation routes."""

from __future__ import annotations

from collections.abc import Callable
from datetime import date, datetime
from typing import Any

from mychecklist.repositories.task_repository import TaskRepository
from mychecklist.services.task_service import filter_and_sort, query_view
from mychecklist.theme import COMPONENTS, DARK_COLORS, FONTS, SPACING, WINDOW
from mychecklist.ui.widgets.task_cards import TaskCardList

VIEW_COPY = {
    "today": ("Today", "Plan and complete the work due today."),
    "upcoming": ("Upcoming", "Plan ahead with future deadlines and scheduled work."),
    "overdue": ("Overdue", "Resolve incomplete tasks whose due date or time has passed."),
    "all": ("All Tasks", "Browse and manage your complete active task collection."),
    "completed": ("Completed", "Review finished work and preserved task history."),
}


class TaskListView:
    """Render one route using persisted rows and reusable task cards."""

    def __init__(
        self,
        parent: Any,
        ctk_module: Any,
        *,
        view: str,
        repository: TaskRepository,
        task_service: Any,
        category_names: dict[int, str],
        today: Callable[[], date],
        now: Callable[[], datetime] | None = None,
        on_edit: Callable[[Any], None],
        confirm_delete: Callable[[], bool],
        on_error: Callable[[str], None],
        show_error: Callable[[str], None] | None = None,
        on_add_task: Callable[[Callable[[], None]], None] | None = None,
    ) -> None:
        if view not in VIEW_COPY:
            raise ValueError(f"unsupported task-list view: {view}")
        self.parent = parent
        self.ctk = ctk_module
        self.view = view
        self.repository = repository
        self.task_service = task_service
        self.category_names = category_names
        self.today = today
        self.now = now or datetime.now
        self.on_edit = on_edit
        self.confirm_delete = confirm_delete
        self.on_error = on_error
        self.show_error = show_error or on_error
        self.on_add_task = on_add_task or (lambda _refresh: None)
        self.search = ""
        self.category_id: int | None = None
        self.priority: str | None = None
        self.sort_by = "due"
        self._build()
        self.refresh()

    def _build(self) -> None:
        title, helper = VIEW_COPY[self.view]
        self.container = self.ctk.CTkFrame(self.parent, fg_color=DARK_COLORS["bg.canvas"])
        self.container.grid(row=0, column=0, sticky="nsew")
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_columnconfigure(1, weight=0)
        self.container.grid_rowconfigure(3, weight=1)
        self.title_label = self.ctk.CTkLabel(
            self.container, text=title, anchor="w", font=FONTS["display"],
            text_color=DARK_COLORS["text.primary"],
        )
        self.title_label.grid(row=0, column=0, padx=SPACING["space.5"], pady=(SPACING["space.5"], 0), sticky="ew")
        self.add_button = self.ctk.CTkButton(
            self.container,
            text="+ Add Task",
            **COMPONENTS["primary_button"],
            height=WINDOW["control_height"],
            command=lambda: self.on_add_task(self.refresh),
        )
        self.add_button.grid(
            row=0, column=1, padx=(SPACING["space.2"], SPACING["space.5"]),
            pady=(SPACING["space.5"], 0), sticky="e",
        )
        self.helper_label = self.ctk.CTkLabel(
            self.container, text=helper, anchor="w", font=FONTS["body"],
            text_color=DARK_COLORS["text.secondary"],
        )
        self.helper_label.grid(row=1, column=0, padx=SPACING["space.5"], pady=SPACING["space.2"], sticky="ew")
        self.filter_frame = self.ctk.CTkFrame(
            self.container, fg_color=DARK_COLORS["bg.surface"],
            corner_radius=WINDOW["panel_radius"],
            border_width=1 if self.view == "overdue" else 0,
            border_color=DARK_COLORS["status.warning"],
        )
        self.filter_frame.grid(row=2, column=0, padx=SPACING["space.5"], pady=SPACING["space.2"], sticky="ew")
        self.filter_frame.grid_columnconfigure(0, weight=1)
        self.search_entry = self.ctk.CTkEntry(
            self.filter_frame, placeholder_text="Search tasks by title",
            **{**COMPONENTS["input"], "height": WINDOW["search_height"]},
        )
        self.search_entry.grid(row=0, column=0, columnspan=4, padx=SPACING["space.3"], pady=SPACING["space.3"], sticky="ew")
        if hasattr(self.search_entry, "bind"):
            self.search_entry.bind("<Return>", lambda _event: self.refresh())
        if hasattr(self.container, "bind"):
            self.container.bind("<Control-n>", lambda _event: self.on_add_task(self.refresh))
        self.category_combo = self.ctk.CTkComboBox(
            self.filter_frame, values=["All categories", *self.category_names.values()],
            width=112, **COMPONENTS["input"],
            command=self._category_changed,
        )
        self.category_combo.set("All categories")
        self.category_combo.grid(row=1, column=0, padx=(SPACING["space.3"], SPACING["space.1"]), pady=(0, SPACING["space.3"]), sticky="ew")
        self.priority_combo = self.ctk.CTkComboBox(
            self.filter_frame, values=["All priorities", "low", "medium", "high"],
            width=112, **COMPONENTS["input"],
            command=self._priority_changed,
        )
        self.priority_combo.set("All priorities")
        self.priority_combo.grid(row=1, column=1, padx=SPACING["space.1"], pady=(0, SPACING["space.3"]), sticky="ew")
        self.sort_combo = self.ctk.CTkComboBox(
            self.filter_frame, values=["Due date", "Priority", "Created date"],
            width=112, **COMPONENTS["input"],
            command=self._sort_changed,
        )
        self.sort_combo.set("Due date")
        self.sort_combo.grid(row=1, column=2, padx=SPACING["space.1"], pady=(0, SPACING["space.3"]), sticky="ew")
        self.apply_button = self.ctk.CTkButton(
            self.filter_frame, text="Apply", width=72, command=self.refresh, **COMPONENTS["primary_button"],
        )
        self.apply_button.grid(row=1, column=3, padx=SPACING["space.1"], pady=(0, SPACING["space.3"]))
        self.clear_button = self.ctk.CTkButton(
            self.filter_frame, text="Clear filters", width=100, command=self.clear_filters,
            **COMPONENTS["secondary_button"],
        )
        self.clear_button.grid(row=1, column=4, padx=(SPACING["space.1"], SPACING["space.3"]), pady=(0, SPACING["space.3"]))
        self.list_frame = self.ctk.CTkScrollableFrame(self.container, fg_color="transparent")
        self.list_frame.grid(row=3, column=0, padx=SPACING["space.3"], pady=SPACING["space.3"], sticky="nsew")
        self.list_frame.grid_columnconfigure(0, weight=1)
        self.empty_label = self.ctk.CTkLabel(
            self.list_frame, text="", anchor="center", font=FONTS["body"],
            text_color=DARK_COLORS["text.muted"],
        )

    def _load_rows(self) -> list[Any]:
        return query_view(self.repository, self.view, self.today(), self.now())

    def refresh(self) -> None:
        try:
            source_rows = self._load_rows()
            rows = filter_and_sort(
                source_rows, search=self.search_entry.get().strip(),
                category_id=self.category_id, priority=self.priority, sort_by=self.sort_by,
            )
        except Exception as error:
            self._show_error_state(str(error))
            return
        if self.view == "today" and hasattr(self.helper_label, "configure"):
            self.helper_label.configure(
                text=f"{len(rows)} task{'s' if len(rows) != 1 else ''} planned for today."
            )
        elif self.view == "completed" and hasattr(self.helper_label, "configure"):
            self.helper_label.configure(
                text=f"{len(rows)} completed occurrence{'s' if len(rows) != 1 else ''} in your history."
            )
        for child in self.list_frame.winfo_children():
            child.destroy()
        if not rows:
            self._render_empty_state()
            self.cards = []
            return
        self.cards = TaskCardList(
            self.list_frame, self.ctk, row_loader=self._load_rows,
            task_service=self.task_service, category_names=self.category_names,
            on_edit=self.on_edit, confirm_delete=self._confirm_delete,
            on_error=self.on_error, on_refresh=self.refresh,
        )
        self.cards.refresh()

    def _render_empty_state(self) -> None:
        empty = self.ctk.CTkFrame(
            self.list_frame, fg_color=DARK_COLORS["bg.surface"],
            corner_radius=WINDOW["panel_radius"],
        )
        empty.grid(row=0, column=0, padx=SPACING["space.5"], pady=SPACING["space.7"], sticky="ew")
        empty.grid_columnconfigure(0, weight=1)
        filtered = self._filters_active()
        self.ctk.CTkLabel(
            empty, text="No matching tasks" if filtered else "Nothing on your list yet",
            font=FONTS["heading"], text_color=DARK_COLORS["text.primary"],
        ).grid(row=0, column=0, padx=SPACING["space.5"], pady=(SPACING["space.5"], SPACING["space.1"]))
        self.ctk.CTkLabel(
            empty,
            text="Try clearing a filter to see more tasks." if filtered
            else "Add your first task to start organizing your day.",
            font=FONTS["body"], text_color=DARK_COLORS["text.secondary"],
        ).grid(row=1, column=0, padx=SPACING["space.5"], pady=SPACING["space.1"])
        if not filtered:
            self.ctk.CTkButton(
                empty, text="+ Add Task", command=lambda: self.on_add_task(self.refresh),
                **COMPONENTS["primary_button"],
            ).grid(row=2, column=0, padx=SPACING["space.5"], pady=(SPACING["space.2"], SPACING["space.5"]))

    def _filters_active(self) -> bool:
        return bool(self.search_entry.get().strip() or self.category_id is not None or self.priority is not None)

    def _category_changed(self, value: str) -> None:
        self.category_id = next(
            (key for key, name in self.category_names.items() if name == value), None
        )

    def _priority_changed(self, value: str) -> None:
        self.priority = None if value == "All priorities" else value

    def _sort_changed(self, value: str) -> None:
        self.sort_by = {"Due date": "due", "Priority": "priority", "Created date": "created"}[value]

    def clear_filters(self) -> None:
        self.search_entry.delete(0, "end")
        self.category_combo.set("All categories")
        self.priority_combo.set("All priorities")
        self.sort_combo.set("Due date")
        self.search = ""
        self.category_id = None
        self.priority = None
        self.sort_by = "due"
        self.refresh()

    def _show_error_state(self, message: str) -> None:
        for child in self.list_frame.winfo_children():
            child.destroy()
        label = self.ctk.CTkLabel(
            self.list_frame, text=f"Unable to load tasks: {message}",
            anchor="center", font=FONTS["body"], text_color=DARK_COLORS["status.danger"],
        )
        label.grid(row=0, column=0, padx=SPACING["space.5"], pady=SPACING["space.5"])
        retry = self.ctk.CTkButton(self.list_frame, text="Retry", command=self.refresh)
        retry.grid(row=1, column=0, padx=SPACING["space.5"], pady=SPACING["space.2"])
        self.show_error(message)

    def _confirm_delete(self) -> bool:
        return self.confirm_delete()


def build_task_route_handlers(
    *,
    ctk_module: Any,
    repository: TaskRepository,
    task_service: Any,
    category_names: dict[int, str],
    today: Callable[[], date],
    now: Callable[[], datetime] | None,
    on_edit: Callable[[Any], None],
    confirm_delete: Callable[[], bool],
    on_error: Callable[[str], None],
    on_add_task: Callable[[Callable[[], None]], None] | None = None,
) -> dict[str, Callable[[Any], None]]:
    """Build shell-compatible handlers for the five task-list routes."""
    views: dict[str, TaskListView] = {}

    def handler(route: str) -> Callable[[Any], None]:
        def render(parent: Any) -> None:
            views[route] = TaskListView(
                parent, ctk_module, view=route, repository=repository,
                task_service=task_service, category_names=category_names,
                today=today, now=now, on_edit=on_edit,
                confirm_delete=confirm_delete, on_error=on_error,
                show_error=on_error,
                on_add_task=on_add_task,
            )
        return render

    return {route: handler(route) for route in VIEW_COPY}
