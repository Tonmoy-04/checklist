"""Statistics screen backed by persisted occurrence aggregates."""

from __future__ import annotations

from collections.abc import Callable
from datetime import date
from typing import Any

from mychecklist.services.statistics_service import StatisticsService
from mychecklist.theme import DARK_COLORS, FONTS, SPACING, WINDOW


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
        self.container.grid_columnconfigure(1, weight=1)
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
        self._label("Statistics", DARK_COLORS["text.primary"], FONTS["display"], 0, 0, 2)
        self._label("A clear view of your progress and completed work.", DARK_COLORS["text.secondary"], FONTS["body"], 1, 0, 2)
        cards = (
            ("Due today", summary["due_today"], DARK_COLORS["accent.primary"]),
            ("Completed today", summary["completed_today"], DARK_COLORS["status.success"]),
            ("Remaining today", summary["remaining_today"], DARK_COLORS["status.warning"]),
            ("Completion rate", f"{summary['completion_rate']:.0f}%", DARK_COLORS["accent.primary"]),
        )
        for index, (label, value, color) in enumerate(cards):
            self._metric_card(label, value, color, row=2 + index // 2, column=index % 2)
        self._section(
            "History",
            f"Last 7 days: {summary['completed_last_7_days']} completed\n"
            f"Last 30 days: {summary['completed_last_30_days']} completed",
            row=4,
        )
        self._section(
            "Breakdown",
            "Categories: " + self._format_breakdown(summary["category_breakdown"]) + "\n"
            "Priorities: " + self._format_breakdown(summary["priority_breakdown"]),
            row=5,
        )

    def _format_breakdown(self, values: dict[str, int]) -> str:
        return ", ".join(f"{key}: {value}" for key, value in sorted(values.items())) or "No completed tasks"

    def _label(self, text: str, color: str, font: Any = None, row: int | None = None,
               column: int = 0, columnspan: int = 1) -> None:
        label = self.ctk.CTkLabel(
            self.container, text=text, anchor="w", text_color=color, font=font or FONTS["body"],
        )
        label.grid(row=row if row is not None else len(self.container.winfo_children()), column=column,
                   columnspan=columnspan,
                   padx=SPACING["space.5"], pady=SPACING["space.2"], sticky="ew")

    def _metric_card(self, label: str, value: Any, color: str, *, row: int, column: int) -> None:
        card = self.ctk.CTkFrame(
            self.container, fg_color=DARK_COLORS["bg.surface"],
            border_width=1, border_color=DARK_COLORS["border.default"],
            corner_radius=WINDOW["card_radius"],
        )
        card.grid(row=row, column=column, padx=SPACING["space.2"], pady=SPACING["space.2"], sticky="nsew")
        self.ctk.CTkLabel(card, text=str(value), font=FONTS["heading"], text_color=color).grid(
            row=0, column=0, padx=SPACING["space.3"], pady=(SPACING["space.3"], 0), sticky="w"
        )
        self.ctk.CTkLabel(card, text=label, font=FONTS["caption"], text_color=DARK_COLORS["text.secondary"]).grid(
            row=1, column=0, padx=SPACING["space.3"], pady=(0, SPACING["space.3"]), sticky="w"
        )

    def _section(self, title: str, text: str, *, row: int) -> None:
        section = self.ctk.CTkFrame(self.container, fg_color=DARK_COLORS["bg.surface"], corner_radius=WINDOW["panel_radius"])
        section.grid(row=row, column=0, columnspan=2, padx=SPACING["space.5"], pady=SPACING["space.2"], sticky="ew")
        self.ctk.CTkLabel(section, text=title, font=FONTS["label"], text_color=DARK_COLORS["text.primary"]).grid(
            row=0, column=0, padx=SPACING["space.3"], pady=(SPACING["space.3"], 0), sticky="w"
        )
        self.ctk.CTkLabel(section, text=text, font=FONTS["body_small"], text_color=DARK_COLORS["text.secondary"], justify="left").grid(
            row=1, column=0, padx=SPACING["space.3"], pady=(SPACING["space.1"], SPACING["space.3"]), sticky="w"
        )
