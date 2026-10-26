"""Task editor dialog with validation and dirty-form protection."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from datetime import date
from typing import Any

from mychecklist.services.validation import ValidationError, validate_task_input
from mychecklist.theme import COMPONENTS, DARK_COLORS, FONTS, SPACING, WINDOW

REMINDER_OPTIONS = {
    "None": None,
    "At due time": 0,
    "5 minutes before": 5,
    "15 minutes before": 15,
    "30 minutes before": 30,
    "1 hour before": 60,
}


class TaskEditorDialog:
    """Create/edit task fields and submit normalized values to a caller."""

    def __init__(
        self,
        parent: Any,
        ctk_module: Any,
        *,
        categories: Mapping[int, str],
        on_save: Callable[[Any], None],
        initial: Mapping[str, Any] | None = None,
        confirm_discard: Callable[[], bool] | None = None,
        show_error: Callable[[str], None] | None = None,
    ) -> None:
        self.parent = parent
        self.ctk = ctk_module
        self.categories = dict(categories)
        self.on_save = on_save
        self.confirm_discard = confirm_discard
        self.show_error = show_error or (lambda message: None)
        self._closed = False
        self._initial = dict(initial or {})
        self.dialog = self.ctk.CTkToplevel(parent)
        self._build()
        self._load_initial()
        self.dialog.protocol("WM_DELETE_WINDOW", self.cancel)
        self.dialog.transient(parent)
        self.dialog.grab_set()

    def _build(self) -> None:
        self.dialog.title(
            "Edit Task" if self._initial.get("id") or self._initial.get("series_id") else "Add Task"
        )
        self.dialog.geometry("520x520")
        self.dialog.minsize(WINDOW["modal_min_width"], 480)
        self.dialog.configure(fg_color=DARK_COLORS["bg.surface"])
        self.dialog.grid_columnconfigure(1, weight=1)

        self._entries: dict[str, Any] = {}
        self._combos: dict[str, Any] = {}
        fields = (
            ("title", "Title"),
            ("due_date", "Due date (YYYY-MM-DD)"),
            ("due_time", "Due time (HH:MM, optional)"),
        )
        for row, (key, label) in enumerate(fields):
            self.ctk.CTkLabel(self.dialog, text=label + (" *" if key in {"title", "due_date"} else ""),
                              font=FONTS["label"],
                              text_color=DARK_COLORS["text.primary"]).grid(
                row=row, column=0, padx=SPACING["space.3"], pady=SPACING["space.2"], sticky="w"
            )
            entry = self.ctk.CTkEntry(self.dialog, **COMPONENTS["input"])
            entry.grid(row=row, column=1, padx=SPACING["space.3"], pady=SPACING["space.2"], sticky="ew")
            self._entries[key] = entry
        if hasattr(self._entries["title"], "bind"):
            self._entries["title"].bind("<Return>", lambda _event: self.save())

        options = (
            ("category_id", "Category", [f"{key}: {value}" for key, value in self.categories.items()]),
            ("priority", "Priority", ["low", "medium", "high"]),
            ("recurrence", "Recurrence", ["none", "daily", "weekly", "monthly"]),
            ("reminder_offset_minutes", "Reminder", list(REMINDER_OPTIONS)),
        )
        for row, (key, label, values) in enumerate(options, start=len(fields)):
            self.ctk.CTkLabel(self.dialog, text=label, font=FONTS["label"],
                              text_color=DARK_COLORS["text.primary"]).grid(
                row=row, column=0, padx=SPACING["space.3"], pady=SPACING["space.2"], sticky="w"
            )
            combo = self.ctk.CTkComboBox(self.dialog, values=values, **COMPONENTS["input"])
            combo.grid(row=row, column=1, padx=SPACING["space.3"], pady=SPACING["space.2"], sticky="ew")
            self._combos[key] = combo

        button_row = len(fields) + len(options)
        self.ctk.CTkButton(self.dialog, text="Cancel", command=self.cancel,
                           **COMPONENTS["secondary_button"]).grid(
            row=button_row, column=0, padx=SPACING["space.3"], pady=SPACING["space.5"], sticky="ew"
        )
        self.ctk.CTkButton(self.dialog, text="Save", command=self.save,
                           **COMPONENTS["primary_button"]).grid(
            row=button_row, column=1, padx=SPACING["space.3"], pady=SPACING["space.5"], sticky="ew"
        )

    def _load_initial(self) -> None:
        values = {
            "title": self._initial.get("title", ""),
            "due_date": self._initial.get("due_date", date.today().isoformat()),
            "due_time": self._initial.get("due_time") or "",
        }
        for key, value in values.items():
            self._entries[key].insert(0, str(value))
        category_id = self._initial.get("category_id")
        self._combos["category_id"].set(
            f"{category_id}: {self.categories[category_id]}" if category_id in self.categories else ""
        )
        self._combos["priority"].set(self._initial.get("priority", "medium"))
        self._combos["recurrence"].set(self._initial.get("recurrence", "none"))
        reminder = self._initial.get("reminder_offset_minutes")
        reminder_label = next((label for label, value in REMINDER_OPTIONS.items() if value == reminder), "None")
        self._combos["reminder_offset_minutes"].set(reminder_label)
        self._saved_snapshot = self._snapshot()

    def _snapshot(self) -> dict[str, str]:
        return {
            **{key: widget.get() for key, widget in self._entries.items()},
            **{key: widget.get() for key, widget in self._combos.items()},
        }

    def _values(self) -> dict[str, Any]:
        snapshot = self._snapshot()
        category_text = snapshot["category_id"].split(":", 1)[0].strip()
        try:
            category_id = int(category_text)
        except ValueError:
            category_id = 0
        return {
            "title": snapshot["title"],
            "due_date": snapshot["due_date"],
            "due_time": snapshot["due_time"],
            "category_id": category_id,
            "priority": snapshot["priority"],
            "recurrence": snapshot["recurrence"],
            "reminder_offset_minutes": REMINDER_OPTIONS.get(snapshot["reminder_offset_minutes"]),
        }

    def save(self) -> bool:
        try:
            validated = validate_task_input(**self._values())
        except ValidationError as error:
            self.show_error(str(error))
            self._focus_first_invalid(error)
            return False
        try:
            self.on_save(validated)
        except Exception as error:
            self.show_error(str(error))
            return False
        self.close()
        return True

    def _focus_first_invalid(self, error: ValidationError) -> None:
        field = next(iter(error.errors), None)
        widget = self._entries.get(field) or self._combos.get(field)
        if widget is not None and hasattr(widget, "focus_set"):
            widget.focus_set()

    def cancel(self) -> bool:
        if self._snapshot() != self._saved_snapshot:
            confirmed = self.confirm_discard() if self.confirm_discard else self._ask_discard()
            if not confirmed:
                return False
        self.close()
        return True

    def _ask_discard(self) -> bool:
        from tkinter import messagebox
        return bool(messagebox.askyesno("Discard changes?", "Discard unsaved task changes?", parent=self.dialog))

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        self.dialog.grab_release()
        self.dialog.destroy()
