from datetime import date

from mychecklist.services.validation import ValidationError, validate_task_input


def test_validate_task_input_normalizes_valid_values() -> None:
    result = validate_task_input(
        title="  Study  ",
        due_date="2026-02-28",
        due_time="09:05",
        category_id=2,
        priority="High",
        recurrence="Monthly",
        reminder_offset_minutes=15,
    )

    assert result.title == "Study"
    assert result.due_date == date(2026, 2, 28)
    assert result.due_time == "09:05"
    assert result.priority == "high"
    assert result.recurrence == "monthly"


def test_validate_task_input_allows_past_date_and_empty_time() -> None:
    result = validate_task_input(
        title="Past task",
        due_date="2000-01-01",
        due_time="",
        category_id=1,
        priority="low",
        recurrence="none",
        reminder_offset_minutes=None,
    )

    assert result.due_date == date(2000, 1, 1)
    assert result.due_time is None


def test_validate_task_input_reports_all_invalid_fields() -> None:
    try:
        validate_task_input(
            title=" ",
            due_date="2026-02-30",
            due_time="25:61",
            category_id=0,
            priority="urgent",
            recurrence="yearly",
            reminder_offset_minutes=10,
        )
    except ValidationError as exc:
        assert set(exc.errors) == {
            "title",
            "due_date",
            "due_time",
            "category_id",
            "priority",
            "recurrence",
            "reminder_offset_minutes",
        }
    else:
        raise AssertionError("invalid task input was accepted")
