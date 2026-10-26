"""Persisted task occurrence cards and their user actions."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from mychecklist.services.task_service import TaskService
from mychecklist.theme import DARK_COLORS, FONTS, SPACING, WINDOW


class TaskCard:
    """Render one occurrence and delegate mutations to the task service."""

    def __init__(
        self,
        parent: Any,
        ctk_module: Any,
        row: Any,
        task_service: TaskService,
        *,
        category_names: dict[int, str],
        on_edit: Callable[[Any], None],
        confirm_delete: Callable[[], bool],
        on_refresh: Callable[[], None],
        on_error: Callable[[str], None],
    ) -> None:
        self.ctk = ctk_module
        self.row = row
        self.task_service = task_service
        self.category_names = category_names
        self.on_edit = on_edit
        self.confirm_delete = confirm_delete
        self.on_refresh = on_refresh
        self.on_error = on_error
        self._status = row["status"]
        self.frame = self.ctk.CTkFrame(
            parent,
            corner_radius=WINDOW["card_radius"],
            fg_color=DARK_COLORS["bg.surface"],
            border_width=1,
            border_color=(
                DARK_COLORS["status.success"]
                if row["status"] == "completed"
                else DARK_COLORS["border.default"]
            ),
            height=WINDOW["task_row_min_height"],
        )
        self.frame.grid_columnconfigure(1, weight=1)
        self._build()

    def _build(self) -> None:
        self.checkbox = self.ctk.CTkCheckBox(
            self.frame,
            text="",
            width=24,
            command=self.toggle_completion,
            fg_color=DARK_COLORS["accent.primary"],
            hover_color=DARK_COLORS["accent.hover"],
        )
        self.checkbox.grid(row=0, column=0, padx=SPACING["space.3"], pady=SPACING["space.3"])
        if self._status == "completed":
            self.checkbox.select()

        self.title_label = self.ctk.CTkLabel(
            self.frame,
            text=self.row["title"],
            anchor="w",
            font=FONTS["subheading"],
            text_color=DARK_COLORS["text.primary"],
        )
        self.title_label.grid(row=0, column=1, padx=SPACING["space.2"], pady=(SPACING["space.2"], 0), sticky="ew")
        metadata = self._metadata()
        self.metadata_label = self.ctk.CTkLabel(
            self.frame,
            text=metadata,
            anchor="w",
            font=FONTS["body_small"],
            text_color=DARK_COLORS["text.secondary"],
        )
        self.metadata_label.grid(row=1, column=1, padx=SPACING["space.2"], pady=(0, SPACING["space.2"]), sticky="ew")

        self.edit_button = self.ctk.CTkButton(
            self.frame, text="Edit", width=64, height=WINDOW["control_height"],
            fg_color=DARK_COLORS["bg.surface_hover"],
            hover_color=DARK_COLORS["accent.hover"],
            command=lambda: self.on_edit(self.row),
        )
        self.edit_button.grid(row=0, column=2, padx=SPACING["space.1"], pady=SPACING["space.2"])
        self.delete_button = self.ctk.CTkButton(
            self.frame, text="Delete", width=72, height=WINDOW["control_height"],
            fg_color="transparent", text_color=DARK_COLORS["status.danger"],
            hover_color=DARK_COLORS["bg.surface_hover"], command=self.delete,
        )
        self.delete_button.grid(row=0, column=3, padx=SPACING["space.2"], pady=SPACING["space.2"])

    def _metadata(self) -> str:
        category = self.category_names.get(self.row["category_id"], "Unknown category")
        due = self.row["due_date"] + (f" {self.row['due_time']}" if self.row["due_time"] else "")
        status = "Completed" if self.row["status"] == "completed" else "Open"
        recurrence_value = self.row.get("recurrence", "none") if hasattr(self.row, "get") else self.row["recurrence"]
        recurrence = recurrence_value.title() if recurrence_value != "none" else ""
        parts = [category, self.row["priority"].title(), f"Due {due}", status]
        if recurrence:
            parts.append(f"Repeats {recurrence}")
        return "  |  ".join(parts)

    def toggle_completion(self) -> None:
        try:
            if self._status == "completed":
                self.task_service.reopen(self.row["id"])
                self._status = "open"
                if hasattr(self.checkbox, "deselect"):
                    self.checkbox.deselect()
            else:
                self.task_service.complete(self.row["id"])
                self._status = "completed"
                if hasattr(self.checkbox, "select"):
                    self.checkbox.select()
        except Exception as error:
            self.on_error(str(error))
        else:
            self.on_refresh()

    def delete(self) -> None:
        if not self.confirm_delete():
            return
        try:
            self.task_service.cancel_occurrence(self.row["id"])
        except Exception as error:
            self.on_error(str(error))
        else:
            self.on_refresh()

    def destroy(self) -> None:
        self.frame.destroy()


class TaskCardList:
    """Refreshable card collection backed by a row loader."""

    def __init__(
        self,
        parent: Any,
        ctk_module: Any,
        *,
        row_loader: Callable[[], list[Any]],
        task_service: TaskService,
        category_names: dict[int, str],
        on_edit: Callable[[Any], None],
        confirm_delete: Callable[[], bool],
        on_error: Callable[[str], None],
        on_refresh: Callable[[], None] | None = None,
    ) -> None:
        self.parent = parent
        self.ctk = ctk_module
        self.row_loader = row_loader
        self.task_service = task_service
        self.category_names = category_names
        self.on_edit = on_edit
        self.confirm_delete = confirm_delete
        self.on_error = on_error
        self.on_refresh = on_refresh or self.refresh
        self.cards: list[TaskCard] = []

    def refresh(self) -> None:
        for card in self.cards:
            card.destroy()
        self.cards = []
        for index, row in enumerate(self.row_loader()):
            card = TaskCard(
                self.parent, self.ctk, row, self.task_service,
                category_names=self.category_names,
                on_edit=self.on_edit,
                confirm_delete=self.confirm_delete,
                on_refresh=self.on_refresh,
                on_error=self.on_error,
            )
            card.frame.grid(row=index, column=0, padx=SPACING["space.3"], pady=SPACING["space.2"], sticky="ew")
            self.cards.append(card)
