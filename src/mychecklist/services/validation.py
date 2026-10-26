"""Validation for task editor and service inputs."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, time
import re
from typing import Any

ALLOWED_PRIORITIES = frozenset({"low", "medium", "high"})
ALLOWED_RECURRENCES = frozenset({"none", "daily", "weekly", "monthly"})
ALLOWED_REMINDER_OFFSETS = frozenset({0, 5, 15, 30, 60})


@dataclass(frozen=True)
class ValidatedTaskInput:
    """Normalized task values ready for a service or repository."""

    title: str
    due_date: date
    due_time: str | None
    category_id: int
    priority: str
    recurrence: str
    reminder_offset_minutes: int | None


class ValidationError(ValueError):
    """A validation failure with field-specific messages."""

    def __init__(self, errors: dict[str, str]) -> None:
        self.errors = errors
        super().__init__("; ".join(f"{field}: {message}" for field, message in errors.items()))


def validate_title(value: str) -> str:
    if not isinstance(value, str):
        raise ValidationError({"title": "Enter a task title."})
    title = value.strip()
    if not title:
        raise ValidationError({"title": "Enter a task title."})
    if len(title) > 200:
        raise ValidationError({"title": "Task titles must be 200 characters or fewer."})
    return title


def validate_due_date(value: str | date) -> date:
    if isinstance(value, date):
        return value
    if not isinstance(value, str):
        raise ValidationError({"due_date": "Enter a date in YYYY-MM-DD format."})
    try:
        return date.fromisoformat(value.strip())
    except ValueError as exc:
        raise ValidationError({"due_date": "Enter a valid date in YYYY-MM-DD format."}) from exc


def validate_due_time(value: str | time | None) -> str | None:
    if value is None or value == "":
        return None
    if isinstance(value, time):
        return value.strftime("%H:%M")
    if not isinstance(value, str):
        raise ValidationError({"due_time": "Enter a valid time in HH:MM format."})
    normalized = value.strip()
    if not re.fullmatch(r"\d{2}:\d{2}", normalized):
        raise ValidationError({"due_time": "Enter a valid time in HH:MM format."})
    try:
        parsed = time.fromisoformat(normalized)
    except ValueError as exc:
        raise ValidationError({"due_time": "Enter a valid time in HH:MM format."}) from exc
    if parsed.second or parsed.microsecond:
        raise ValidationError({"due_time": "Enter a valid time in HH:MM format."})
    return parsed.strftime("%H:%M")


def validate_category_id(value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValidationError({"category_id": "Choose a valid category."})
    return value


def validate_choice(value: str, field: str, allowed: frozenset[str]) -> str:
    if not isinstance(value, str):
        raise ValidationError({field: f"Choose a valid {field.replace('_', ' ')}."})
    normalized = value.strip().lower()
    if normalized not in allowed:
        raise ValidationError({field: f"Choose a valid {field.replace('_', ' ')}."})
    return normalized


def validate_priority(value: str) -> str:
    return validate_choice(value, "priority", ALLOWED_PRIORITIES)


def validate_recurrence(value: str) -> str:
    return validate_choice(value, "recurrence", ALLOWED_RECURRENCES)


def validate_reminder_offset(value: int | None) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value not in ALLOWED_REMINDER_OFFSETS:
        raise ValidationError({"reminder_offset_minutes": "Choose a supported reminder offset."})
    return value


def validate_task_input(
    *,
    title: str,
    due_date: str | date,
    due_time: str | time | None,
    category_id: Any,
    priority: str,
    recurrence: str,
    reminder_offset_minutes: int | None,
) -> ValidatedTaskInput:
    """Validate and normalize all task editor fields.

    All fields are evaluated before raising so callers can display every
    actionable field error at once.
    """
    errors: dict[str, str] = {}
    values: dict[str, Any] = {}
    validators = (
        ("title", lambda: validate_title(title)),
        ("due_date", lambda: validate_due_date(due_date)),
        ("due_time", lambda: validate_due_time(due_time)),
        ("category_id", lambda: validate_category_id(category_id)),
        ("priority", lambda: validate_priority(priority)),
        ("recurrence", lambda: validate_recurrence(recurrence)),
        ("reminder_offset_minutes", lambda: validate_reminder_offset(reminder_offset_minutes)),
    )
    for field, validator in validators:
        try:
            values[field] = validator()
        except ValidationError as exc:
            errors.update(exc.errors)
    if errors:
        raise ValidationError(errors)
    return ValidatedTaskInput(**values)
