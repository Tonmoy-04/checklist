"""Runtime resource resolution for source and PyInstaller executions."""

from __future__ import annotations

import sys
from pathlib import Path


def resource_path(relative_path: str | Path = "") -> Path:
    """Resolve a read-only bundled resource without using the data directory."""
    relative = Path(relative_path)
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        base = Path(sys._MEIPASS)
    else:
        base = Path(__file__).resolve().parent
    return base / relative
