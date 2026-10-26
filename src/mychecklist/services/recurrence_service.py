"""Deterministic recurrence date calculations."""
from __future__ import annotations

import calendar
from datetime import date, timedelta


def next_occurrence_date(value: date, recurrence: str, interval_count: int = 1) -> date:
    if interval_count < 1:
        raise ValueError("interval_count must be at least 1")
    if recurrence == "none":
        raise ValueError("non-recurring tasks have no next occurrence")
    if recurrence == "daily":
        return value + timedelta(days=interval_count)
    if recurrence == "weekly":
        return value + timedelta(weeks=interval_count)
    if recurrence == "monthly":
        month_index = value.month - 1 + interval_count
        year, month = divmod(month_index, 12)
        year += value.year
        return date(year, month + 1, min(value.day, calendar.monthrange(year, month + 1)[1]))
    raise ValueError(f"unsupported recurrence: {recurrence}")
