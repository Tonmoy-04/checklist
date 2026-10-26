"""Plyer desktop notification adapter."""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class PlyerNotifier:
    def __init__(self, app_name: str = "MyChecklist") -> None:
        self.app_name = app_name

    def __call__(self, *, title: str, message: str) -> bool:
        try:
            from plyer import notification
            notification.notify(title=title, message=message, app_name=self.app_name)
            return True
        except Exception:
            logger.exception("Desktop notification delivery failed")
            return False
