"""Notification provider contract."""
from __future__ import annotations

from typing import Protocol


class NotificationProvider(Protocol):
    def __call__(self, *, title: str, message: str) -> object:
        ...
