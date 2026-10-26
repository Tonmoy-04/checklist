"""Centralized MyChecklist UI design tokens and CustomTkinter setup."""

from __future__ import annotations

from typing import Any

DARK_COLORS = {
    "bg.canvas": "#111318",
    "bg.sidebar": "#171A21",
    "bg.surface": "#1B1F28",
    "bg.surface_hover": "#242A35",
    "bg.input": "#151922",
    "border.default": "#2C3340",
    "text.primary": "#F3F5F8",
    "text.secondary": "#A7B0BF",
    "text.muted": "#788395",
    "accent.primary": "#6D8DFF",
    "accent.hover": "#829DFF",
    "accent.pressed": "#5577EA",
    "status.success": "#43B581",
    "status.warning": "#F0B44D",
    "status.danger": "#F16C75",
    "status.info": "#63B3ED",
    "priority.low": "#63B3ED",
    "priority.medium": "#F0B44D",
    "priority.high": "#F16C75",
}

LIGHT_COLORS = {
    "bg.canvas": "#F5F7FA",
    "bg.sidebar": "#FFFFFF",
    "bg.surface": "#FFFFFF",
    "bg.surface_hover": "#EDF1F7",
    "bg.input": "#F8FAFC",
    "border.default": "#D9E0EA",
    "text.primary": "#182230",
    "text.secondary": "#526173",
    "text.muted": "#7C8999",
    "accent.primary": "#4263D8",
    "accent.hover": "#3454C7",
    "accent.pressed": "#2946B4",
    "status.success": "#18794E",
    "status.warning": "#946200",
    "status.danger": "#C93643",
    "status.info": "#1769AA",
    "priority.low": "#1769AA",
    "priority.medium": "#946200",
    "priority.high": "#C93643",
}

FONTS = {
    "display": ("Segoe UI", 28, "bold"),
    "heading": ("Segoe UI", 20, "bold"),
    "subheading": ("Segoe UI", 16, "bold"),
    "body": ("Segoe UI", 14, "normal"),
    "body_small": ("Segoe UI", 12, "normal"),
    "caption": ("Segoe UI", 11, "normal"),
    "button": ("Segoe UI", 13, "bold"),
    "label": ("Segoe UI", 12, "bold"),
}

SPACING = {
    "space.1": 4,
    "space.2": 8,
    "space.3": 12,
    "space.4": 16,
    "space.5": 24,
    "space.6": 32,
    "space.7": 40,
}

WINDOW = {
    "default_width": 1100,
    "default_height": 720,
    "minimum_width": 850,
    "minimum_height": 580,
    "sidebar_width": 210,
    "content_padding": 24,
    "task_row_min_height": 64,
    "control_height": 36,
    "modal_min_width": 440,
    "modal_max_width": 560,
    "control_radius": 8,
    "card_radius": 12,
    "panel_radius": 14,
    "input_width": 150,
    "search_height": 40,
}

COMPONENTS = {
    "primary_button": {
        "fg_color": DARK_COLORS["accent.primary"],
        "hover_color": DARK_COLORS["accent.hover"],
        "text_color": DARK_COLORS["text.primary"],
        "font": FONTS["button"],
        "corner_radius": WINDOW["control_radius"],
    },
    "secondary_button": {
        "fg_color": DARK_COLORS["bg.surface"],
        "hover_color": DARK_COLORS["bg.surface_hover"],
        "text_color": DARK_COLORS["text.primary"],
        "font": FONTS["button"],
        "corner_radius": WINDOW["control_radius"],
    },
    "input": {
        "fg_color": DARK_COLORS["bg.input"],
        "border_color": DARK_COLORS["border.default"],
        "border_width": 1,
        "height": WINDOW["control_height"],
        "corner_radius": WINDOW["control_radius"],
    },
}


def colors(theme: str = "dark") -> dict[str, str]:
    """Return a copy of the selected color token set."""
    if theme == "dark":
        return DARK_COLORS.copy()
    if theme == "light":
        return LIGHT_COLORS.copy()
    raise ValueError(f"unsupported theme: {theme}")


def configure_customtkinter(ctk_module: Any | None = None) -> Any:
    """Configure CustomTkinter's dark-first global settings.

    The import is lazy so services and token tests do not require a GUI
    dependency. A module argument allows a UI composition root to inject the
    imported CustomTkinter module.
    """
    if ctk_module is None:
        import customtkinter as ctk_module
    ctk_module.set_appearance_mode("dark")
    ctk_module.set_default_color_theme("dark-blue")
    return ctk_module
