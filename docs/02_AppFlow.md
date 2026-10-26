# 02 — Application Flow and State Machine

## 1. Top-level navigation

The main window is a persistent shell with a left sidebar and a content area.

| Route key | Screen title | Data source | Primary purpose |
|---|---|---|---|
| `today` | Today | Incomplete occurrences due today | Daily execution |
| `upcoming` | Upcoming | Incomplete occurrences due after today | Planning ahead |
| `overdue` | Overdue | Incomplete occurrences with past due date/time | Recover missed work |
| `all` | All Tasks | All active occurrences | Browse active work |
| `completed` | Completed | Completed occurrences | History |
| `statistics` | Statistics | Aggregated occurrences | Progress overview |
| `settings` | Settings | Local settings table | Theme, reminders, backup |

The add-task action is available from task-list screens. Task editor and confirmation dialogs are modal child windows. Navigation must not destroy unsaved edits without warning.

## 2. Application lifecycle state machine

```text
START
  -> Resolve %LOCALAPPDATA%\\MyChecklist
  -> Open/create SQLite database
  -> Apply versioned migrations transactionally
  -> Validate database health
  -> Load settings
  -> Render Today
  -> Start reminder scheduler
  -> RUNNING
       -> navigation event -> load selected route
       -> create/edit/delete/complete -> validate -> database transaction -> refresh affected view
       -> close request -> stop scheduler -> flush/close resources -> EXIT
```

Startup failures:
- Cannot create app-data directory: show a blocking diagnostic with the attempted path; offer to open the parent folder if possible; do not silently use a temporary database.
- Database is locked: retry a small bounded number of times; then show recovery instructions and do not overwrite the file.
- Database is corrupt: preserve the original file, offer backup/recovery guidance, and never auto-delete it.
- Migration fails: rollback the migration transaction, preserve the original DB, show the error, and stop normal startup.

## 3. Screen contracts

### Today / Upcoming / Overdue / All Tasks / Completed
Components:
- Page title and concise helper text.
- Search input.
- Category and priority filters.
- Sort selector (due date/time, priority, created date).
- Task rows/cards showing checkbox, title, category, priority, due date/time, recurrence marker, and overdue indicator.
- Add Task button.
- Empty state with helpful message and Add Task action.

Actions:
- **Add Task:** opens editor in create mode.
- **Checkbox:** asks service to complete/reopen occurrence; updates view and statistics.
- **Edit:** opens editor prefilled from persisted record.
- **Delete:** confirmation dialog; Cancel has no side effect.
- **Search/filter/sort:** updates visible results only; must not mutate database.
- **Navigation:** changes route and refreshes data.
- **Completed task:** read-only by default except reopen and delete; edits must be supported only if history semantics are defined.

Empty/error states:
- No tasks: “No tasks here yet” plus an appropriate next action.
- No search results: “No tasks match these filters” plus Clear filters.
- Validation error: inline field message and focus the invalid field.
- Database error: non-destructive error banner/dialog; preserve form values for retry.
- Query failure: keep the previous screen if possible and show retry.

### Task editor dialog
Fields:
- Title (required; max length 200 characters).
- Due date (required, local date, displayed in ISO format in MVP).
- Due time (optional; 24-hour HH:MM).
- Category (predefined values managed locally).
- Priority (`Low`, `Medium`, `High`).
- Recurrence (`None`, `Daily`, `Weekly`, `Monthly`).
- Reminder offset (`None`, `At due time`, `5 minutes`, `15 minutes`, `30 minutes`, `1 hour` before) if reminder configuration is enabled.

Actions:
- **Save:** validate all fields; create/update in one transaction; close only on success.
- **Cancel / window close:** if fields changed, ask whether to discard; otherwise close.
- **Date picker:** choose a date; manually entered ISO date is validated.
- **Time:** validate 24-hour time and reject impossible values.

Error cases:
- Blank title -> inline “Enter a task title.”
- Invalid date -> inline date error; preserve value.
- Invalid time -> inline time error; preserve value.
- Past date -> allowed, because overdue tasks are valid; indicate it will be overdue.
- Database failure -> remain in dialog and preserve input.

### Statistics
Display:
- Due today, completed today, remaining today, completion percentage.
- Completed occurrences over the last 7 and 30 days.
- Category breakdown and priority breakdown.
- Clear no-data state.

Rules:
- Percent = completed due-today occurrences / all due-today occurrences * 100.
- If denominator is zero, show 0%.
- Deleted records do not count. Completed occurrences remain in history.
- All chart values are derived from database queries, not cached UI state.

### Settings
Settings include theme (dark default; light optional), reminder enable/disable, default reminder offset, startup behavior (future enhancement), and database backup/restore.
- Changes apply only after validation.
- Restore requires explicit confirmation and a validated backup file.
- “Reset all data” is not part of MVP.

## 4. Button and keyboard action contract

| Control | Action | Success | Failure |
|---|---|---|---|
| Add Task | Open blank editor | Editor focused on title | Show dialog error |
| Save | Validate and persist | Close editor; refresh views | Keep editor open; show field or DB error |
| Cancel | Close editor | Return to prior screen | If dirty, ask discard confirmation |
| Checkbox | Complete/reopen occurrence | Persist state; refresh counts | Revert checkbox; show error |
| Edit | Open prefilled editor | Fields match DB record | Show error if task no longer exists |
| Delete | Ask confirmation then delete | Remove from active list | Preserve row and show error |
| Clear filters | Reset search/filter values | Full list shown | No database mutation |
| Sidebar item | Navigate | Route title and data update | Keep prior route and show error |
| Backup | Create consistent SQLite backup | Show destination path | Show error; preserve original DB |
| Restore | Validate and replace DB safely | Reopen DB and refresh app | Preserve current DB and show error |
| Close window | Stop timers and close DB | Clean exit | Warn if shutdown cannot complete |

Keyboard:
- `Enter` in title field submits only when the form is valid and not inside a multiline editor.
- `Escape` closes a modal only after dirty-form confirmation when applicable.
- `Tab` / `Shift+Tab` follow visual order.
- Delete actions are never triggered by an unconfirmed keyboard shortcut in MVP.

## 5. Reminder scheduler state machine

```text
APP START
  -> load enabled reminder settings
  -> every 15–30 seconds query due reminders
  -> select incomplete occurrences within reminder window
  -> atomically claim reminder delivery (unique occurrence + reminder kind)
  -> dispatch desktop notification
  -> record delivery outcome
  -> repeat until app shutdown
```

- Do not mark a reminder as delivered before a durable claim/delivery attempt is recorded.
- Duplicate scheduler ticks must not produce duplicate notifications.
- If notification delivery fails, record failure and follow bounded retry policy.
- The app-open scheduler does not guarantee reminders while the process is closed. This limitation must be visible in Settings/help.
