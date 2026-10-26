# 01 — Product Requirements Document (PRD)

- **Product:** MyChecklist
- **Document status:** Baseline specification, v1.0
- **Platform:** Windows desktop
- **Primary user:** One person managing personal, academic, learning, health, and work tasks.
- **Product principle:** Local-first, private-by-default, predictable, and easy to use.

## 1. Problem statement

The user needs one dependable desktop place to capture tasks, schedule them, categorize and prioritize them, mark them complete, receive reminders, and understand progress. A plain text list cannot reliably represent due dates, recurring work, completion history, or statistics. The app must work offline and preserve data across restarts.

## 2. Goals

1. Capture and update tasks quickly without leaving the desktop app.
2. Make today's, upcoming, overdue, all, and completed work easy to distinguish.
3. Support dates, optional times, categories, priorities, and recurring schedules.
4. Preserve completed occurrences and provide useful, explainable statistics.
5. Store data locally with transactional updates and a documented backup path.
6. Keep the code modular and testable for AI-assisted implementation.

## 3. Target persona

**Primary persona — Individual Windows user**
- Uses a Windows PC for university, self-study, and personal tasks.
- Wants a modern dark desktop UI and a normal resizable window.
- May use the app without internet access.
- Does not need teams, shared lists, accounts, cloud sync, or a web service.

No multi-user or organization persona is in scope for v1.

## 4. MVP user stories and acceptance criteria

### TASK-01: Create a task
As a user, I can enter a title, due date, optional due time, category, priority, and recurrence so that the task is stored and visible in the correct view.
- Title is required and whitespace-only titles are rejected.
- Date and optional time are validated before persistence.
- Invalid input produces an actionable message; no invalid row is written.
- The task remains after app restart.

### TASK-02: View and filter tasks
As a user, I can navigate Today, Upcoming, Overdue, All Tasks, Completed, and Statistics.
- Each list has a defined query, stable sort order, and empty state.
- Completed tasks do not appear in active-task views.
- Overdue tasks are incomplete tasks whose due date/time is in the past.

### TASK-03: Complete and reopen a task
As a user, I can mark an occurrence complete and undo that state if needed.
- Completion timestamp is recorded.
- Completing a recurring occurrence schedules its next occurrence exactly once.
- Reopening a recurring occurrence does not silently delete already-created history or create duplicate future occurrences.

### TASK-04: Edit and delete
As a user, I can edit task fields and delete a task after confirmation.
- Canceling a delete confirmation changes nothing.
- Editing validates all fields and preserves the task ID.
- Deletion behavior for recurring series is explicit: deleting one occurrence affects only that occurrence; deleting a series requires a separate confirmed action.

### TASK-05: Reminders
As a user, I can receive a desktop notification for a scheduled task.
- A reminder is delivered at most once per occurrence per configured reminder offset.
- Missed reminders are handled according to the reminder policy in `04_TRD.md`.
- Notification failure is logged and does not crash the UI.
- Reminder behavior when the app is closed is clearly communicated; do not claim background reminders until Windows Task Scheduler integration is implemented and tested.

### TASK-06: Recurrence
As a user, I can repeat a task daily, weekly, or monthly.
- The next occurrence is generated from the scheduled occurrence date, not from the current date.
- Monthly recurrence clamps to the last valid day (e.g., Jan 31 -> Feb 28/29).
- Each occurrence has an independent completion state and timestamp.
- Duplicate next occurrences are prevented by a database constraint or transactional idempotency check.

### TASK-07: Statistics
As a user, I can see today's totals and completion rate plus historical completion summaries.
- Empty denominators display 0%, not an exception.
- Statistics are computed from persisted occurrence data.
- Historical counts distinguish completed occurrences from deleted tasks.

### TASK-08: Data safety
As a user, I can locate, back up, and restore my local data.
- Production database is stored under `%LOCALAPPDATA%\MyChecklist\`.
- Database writes use transactions and parameterized SQL.
- Backup and restore operations explain the destination/source and avoid overwriting without confirmation.

## 5. Product requirements

- Windows 10/11 desktop; offline-first.
- Dark theme is the default. Light theme may be added without changing business logic.
- Keyboard support: Enter submits the add-task form; Tab order is logical; focus is visible.
- All task views show loading-free local data and clear empty/error states.
- No task data leaves the machine.
- UI must not freeze during periodic reminder checks or backup operations.
- Local time is the v1 time basis. Persist due dates as ISO `YYYY-MM-DD`; due times as `HH:MM` 24-hour strings. Store event timestamps as ISO-8601 local timestamps with offset or UTC timestamps consistently; the implementation must choose UTC ISO-8601 for event timestamps and convert for display.

## 6. Success metrics

- A new task can be saved in under 10 seconds using the keyboard.
- 100% of valid create/edit/complete operations survive restart.
- All core workflows have automated tests.
- No uncaught exception for invalid date, invalid time, empty title, or missing task ID.
- A reminder is not duplicated for the same occurrence and reminder schedule.
- Statistics match direct database fixtures in tests.
- Fresh installation opens without an existing database and creates a valid schema.

## 7. Out of Scope (Non-Goals)

The following are explicitly excluded from v1 unless this document is amended:
- User accounts, sign-up/login, OAuth, authentication server, or password storage.
- Multi-user collaboration, teams, sharing, or permissions.
- Cloud sync, remote database, web server, REST/GraphQL API, or third-party task API.
- Row-Level Security (RLS): this is a local SQLite database with no database-server identity boundary.
- Mobile, web, and macOS/Linux UI support.
- AI task planning, LLM integration, calendar-provider integrations, email/SMS messaging.
- Gamification, social feeds, billing, ads, and analytics telemetry.
- Silent destructive migrations or automatic data deletion.
- Guaranteed reminders while the app is closed until a separately tested Windows scheduled-task/background mechanism is implemented.

## 8. MVP release gate

Release only when:
1. The app launches from a clean profile and from an existing database.
2. CRUD, recurrence, reminder deduplication, filters, and statistics pass tests.
3. Database location is outside the installation directory.
4. Backup/restore is tested against a copy of a real database.
5. Packaged `.exe` is tested on a clean Windows account.
6. No known critical data-loss issue remains.
