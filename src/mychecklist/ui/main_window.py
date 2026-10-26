"""Main application shell and navigation lifecycle."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

from mychecklist.theme import DARK_COLORS, FONTS, SPACING, WINDOW

ROUTES = (
    ("today", "Today"),
    ("upcoming", "Upcoming"),
    ("overdue", "Overdue"),
    ("all", "All Tasks"),
    ("completed", "Completed"),
    ("statistics", "Statistics"),
    ("settings", "Settings"),
)


class MainWindow:
    """Compose the persistent sidebar/content shell around a CustomTkinter root."""

    def __init__(
        self,
        root: Any,
        ctk_module: Any,
        *,
        route_handlers: Mapping[str, Callable[[Any], None]] | None = None,
        on_close: Callable[[], None] | None = None,
        reminder_poller: Any | None = None,
    ) -> None:
        self.root = root
        self.ctk = ctk_module
        self.route_handlers = dict(route_handlers or {})
        self.close_callback = on_close
        self.reminder_poller = reminder_poller
        self.current_route = "today"
        self._closed = False
        self._buttons: dict[str, Any] = {}
        self._build_shell()
        self.navigate("today")
        if self.reminder_poller is not None:
            self.reminder_poller.start()

    def _build_shell(self) -> None:
        self.root.title("MyChecklist")
        self.root.geometry(f"{WINDOW['default_width']}x{WINDOW['default_height']}")
        self.root.minsize(WINDOW["minimum_width"], WINDOW["minimum_height"])
        self.root.configure(fg_color=DARK_COLORS["bg.canvas"])
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        self.sidebar = self.ctk.CTkFrame(
            self.root,
            width=WINDOW["sidebar_width"],
            corner_radius=0,
            fg_color=DARK_COLORS["bg.sidebar"],
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_rowconfigure(len(ROUTES) + 1, weight=1)

        self.brand = self.ctk.CTkLabel(
            self.sidebar,
            text="MyChecklist",
            font=FONTS["heading"],
            text_color=DARK_COLORS["text.primary"],
        )
        self.brand.grid(row=0, column=0, padx=SPACING["space.4"], pady=(SPACING["space.5"], SPACING["space.4"]))

        for index, (route, label) in enumerate(ROUTES, start=1):
            button = self.ctk.CTkButton(
                self.sidebar,
                text=label,
                anchor="w",
                height=WINDOW["control_height"],
                corner_radius=WINDOW["control_radius"],
                fg_color="transparent",
                hover_color=DARK_COLORS["bg.surface_hover"],
                text_color=DARK_COLORS["text.secondary"],
                font=FONTS["body"],
                command=lambda route_key=route: self.navigate(route_key),
            )
            button.grid(row=index, column=0, padx=SPACING["space.2"], pady=SPACING["space.1"], sticky="ew")
            self._buttons[route] = button

        self.content = self.ctk.CTkFrame(
            self.root,
            corner_radius=0,
            fg_color=DARK_COLORS["bg.canvas"],
        )
        self.content.grid(row=0, column=1, padx=0, pady=0, sticky="nsew")
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

    def navigate(self, route: str) -> None:
        if route not in dict(ROUTES):
            raise ValueError(f"unsupported route: {route}")
        self.current_route = route
        for route_key, button in self._buttons.items():
            active = route_key == route
            button.configure(
                fg_color=DARK_COLORS["accent.primary"] if active else "transparent",
                text_color=DARK_COLORS["text.primary"] if active else DARK_COLORS["text.secondary"],
            )
        handler = self.route_handlers.get(route)
        if handler is not None:
            handler(self.content)

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        if self.reminder_poller is not None:
            self.reminder_poller.stop()
        if self.close_callback is not None:
            self.close_callback()
        self.root.destroy()
