"""Reminder claiming and delivery orchestration."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Callable

from mychecklist.repositories.reminder_repository import ReminderRepository


class ReminderService:
    def __init__(self, repository: ReminderRepository, notifier: Callable[..., object],
                 clock: Callable[[], datetime] | None = None,
                 notify_missed_reminders: bool = True,
                 max_attempts: int = 3) -> None:
        self.repository = repository
        self.notifier = notifier
        self.clock = clock or (lambda: datetime.now(timezone.utc))
        self.notify_missed_reminders = notify_missed_reminders
        self.max_attempts = max_attempts

    def process_due(self, offset_minutes: int = 0) -> int:
        now = self.clock()
        now_text = now.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
        rows = self.repository.claim_due(
            now_text, offset_minutes,
            notify_missed=self.notify_missed_reminders,
            max_attempts=self.max_attempts,
        )
        for row in rows:
            try:
                result = self.notifier(title="MyChecklist", message=row["title"])
                delivered = result is not False
                self.repository.record(row["id"], offset_minutes, delivered=delivered,
                                       error_code=None if delivered else "provider_failed")
            except Exception:
                self.repository.record(row["id"], offset_minutes, delivered=False, error_code="provider_exception")
        return len(rows)
