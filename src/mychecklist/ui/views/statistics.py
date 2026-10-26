"""Statistics screen backed by persisted occurrence aggregates."""

from __future__ import annotations

from collections.abc import Callable
from datetime import date
from typing import Any

from mychecklist.services.statistics_service import StatisticsService
from mychecklist.theme import DARK_COLORS, FONTS, SPACING


class StatisticsView:
    def __init__(self, parent: Any, ctk_module: Any, *, connection: Any,
                 today: Callable[[], date], on_error: Callable[[str], None]) -> None:
        self.ctk = ctk_module
        self.connection = connection
        self.today = today
        self.on_error = on_error
        self.container = self.ctk.CTkFrame(parent, fg_color=DARK_COLORS["bg.canvas"])
        self.container.grid(row=0, column=0, sticky="nsew")
        self.container.grid_columnconfigure(0, weight=1)
        self.refresh()

    def refresh(self) -> None:
        for child in self.container.winfo_children():
            child.destroy()
        try:
            summary = StatisticsService(self.connection).summary(self.today())
        except Exception as error:
            self.on_error(str(error))
            self._label(f"Unable to load statistics: {error}", DARK_COLORS["status.danger"])
            return
        self._label("Statistics", DARK_COLORS["text.primary"], FONTS["display"])
        lines = [
            f"Due today: {summary['due_today']}",
            f"Completed today: {summary['completed_today']}",
            f"Remaining today: {summary['remaining_today']}",
            f"Completion rate: {summary['completion_rate']:.0f}%",
            f"Completed last 7 days: {summary['completed_last_7_days']}",
            f"Completed last 30 days: {summary['completed_last_30_days']}",
            "Categories: " + self._format_breakdown(summary["category_breakdown"]),
            "Priorities: " + self._format_breakdown(summary["priority_breakdown"]),
        ]
        for line in lines:
            self._label(line, DARK_COLORS["text.secondary"], FONTS["body"])

    def _format_breakdown(self, values: dict[str, int]) -> str:
        return ", ".join(f"{key}: {value}" for key, value in sorted(values.items())) or "No completed tasks"

    def _label(self, text: str, color: str, font: Any = None) -> None:
        label = self.ctk.CTkLabel(
            self.container, text=text, anchor="w", text_color=color, font=font or FONTS["body"],
        )
        label.grid(row=len(self.container.winfo_children()), column=0,
                   padx=SPACING["space.5"], pady=SPACING["space.2"], sticky="ew")
