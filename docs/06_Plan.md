# 06 — Implementation Plan

> The coding agent must update this file after every completed checklist item. Mark an item complete only after the implementation and its verification both succeed. Record the date, files changed, test command, and result in the Progress Log.

## Phase 0 — Specification and repository foundation

- [x] **P0.1** Read all six documents and identify conflicts before coding.
- [x] **P0.2** Create the `src/mychecklist/` package and `tests/` structure from `04_TRD.md`.
- [ ] **P0.3** Add pinned runtime/dev dependencies and `pyproject.toml`.
- [ ] **P0.4** Add `.gitignore` for `.venv/`, `__pycache__/`, `.pytest_cache/`, build artifacts, logs, and local DB files.
- [ ] **P0.5** Add a README with setup, run, test, data-location, backup, and known reminder limitations.
- [ ] **P0.6** Add logging and configuration helpers; verify AppData paths without writing beside the executable.

## Phase 1 — Database and data model (no UI dependency)

- [ ] **P1.1** Implement SQLite connection factory with foreign keys and busy timeout.
- [ ] **P1.2** Implement versioned migrations and schema creation from `05_Schema.md`.
- [ ] **P1.3** Seed built-in categories idempotently.
- [ ] **P1.4** Implement category repository and validation.
- [ ] **P1.5** Implement task-series and occurrence repositories with parameterized SQL.
- [ ] **P1.6** Implement task create/update/cancel/delete semantics and transaction boundaries.
- [ ] **P1.7** Implement recurrence date calculator (daily, weekly, monthly end-of-month clamp).
- [ ] **P1.8** Implement completion/reopen and idempotent next-occurrence creation.
- [ ] **P1.9** Implement indexes and database integrity checks.
- [ ] **P1.10** Add unit/integration tests for schema, constraints, migrations, and repository CRUD.

## Phase 2 — Application services

- [ ] **P2.1** Implement input validation for title, date, time, category, priority, recurrence, and reminder offsets.
- [ ] **P2.2** Implement task service independent of CustomTkinter.
- [ ] **P2.3** Implement view query rules for Today, Upcoming, Overdue, All Tasks, and Completed.
- [ ] **P2.4** Implement search, category/priority filters, and stable sorting.
- [ ] **P2.5** Implement statistics service and test zero-denominator/historical calculations.
- [ ] **P2.6** Implement reminder service with injected clock and deduplicated delivery records.
- [ ] **P2.7** Implement notification interface and Plyer adapter with failure handling.
- [ ] **P2.8** Implement SQLite online backup and validated restore flow.
- [ ] **P2.9** Add service tests for edge cases, reminder retry policy, and recurring task idempotency.

## Phase 3 — UI integration

- [ ] **P3.1** Implement centralized design tokens and CustomTkinter theme setup from `03_UI_Spec.md`.
- [ ] **P3.2** Implement main window, sidebar navigation, responsive content area, and close lifecycle.
- [ ] **P3.3** Implement task editor dialog with field validation and unsaved-change confirmation.
- [ ] **P3.4** Implement task cards, completion/reopen, edit, and confirmed deletion.
- [ ] **P3.5** Implement Today, Upcoming, Overdue, All Tasks, and Completed views.
- [ ] **P3.6** Implement search/filter/sort and clear-filters behavior.
- [ ] **P3.7** Implement Statistics view and category/priority summaries.
- [ ] **P3.8** Implement Settings view for theme/reminders/backup/restore.
- [ ] **P3.9** Integrate reminder polling without blocking UI or touching Tk widgets from worker threads.
- [ ] **P3.10** Verify empty states, error states, keyboard navigation, and window minimum size.

## Phase 4 — Edge-case and regression tests

- [ ] **P4.1** Test blank/whitespace title and title length boundaries.
- [ ] **P4.2** Test invalid date/time, leap day, and past due dates.
- [ ] **P4.3** Test monthly recurrence on days 28–31, leap years, and year rollover.
- [ ] **P4.4** Test double-click completion and repeated scheduler ticks for duplicate prevention.
- [ ] **P4.5** Test reopening recurring tasks and deleting one occurrence vs stopping a series.
- [ ] **P4.6** Test no tasks, no search results, empty statistics, and filters with no matches.
- [ ] **P4.7** Test locked/corrupt DB, failed migration rollback, and missing app-data directory.
- [ ] **P4.8** Test backup/restore with valid, corrupt, incompatible, and currently-open database files.
- [ ] **P4.9** Test notification provider failure and missed-reminder policy.
- [ ] **P4.10** Run full test suite and fix defects without weakening acceptance criteria.

## Phase 5 — Packaging and release validation

- [ ] **P5.1** Implement package entry point (`python -m mychecklist`).
- [ ] **P5.2** Build a Windows GUI executable with PyInstaller.
- [ ] **P5.3** Test packaged assets, AppData DB creation, and clean shutdown.
- [ ] **P5.4** Test upgrade behavior with an existing database and migration.
- [ ] **P5.5** Test on a clean Windows account and at 100%, 125%, and 150% display scaling.
- [ ] **P5.6** Document known limitations, version, backup/restore steps, and release checklist.

## Definition of Done for every item

1. Specification and relevant acceptance criteria are understood.
2. Implementation is limited to the current item and its dependencies.
3. Tests are added or updated for changed behavior.
4. Relevant tests pass; failures are reported honestly.
5. No unrelated refactor or dependency change is included.
6. This plan is updated with completion status and verification evidence.
7. No item is marked complete merely because code was written.

## Progress Log

| Date | Plan item | Files changed | Verification | Result |
|---|---|---|---|---|
| 2026-10-27 | P0.1 | `docs/06_Plan.md` | Read `docs/01_PRD.md` through `docs/06_Plan.md`, plus `README.md`, `CLAUDE.md`, and `.cursorrules`; inspected workspace contents | Passed; no specification conflicts found, and implementation has not started. |
| 2026-10-27 | P0.2 | `src/mychecklist/**/__init__.py`, `tests/unit/.gitkeep`, `tests/integration/.gitkeep`, `tests/ui/.gitkeep` | Structural PowerShell check; `python -m compileall -q src\mychecklist`; explicit generated-cache cleanup | Passed; all documented package boundaries and test directories are present, with no feature modules created. |

## Decision log

- **D-001:** Local-first single-user Windows app; no auth, server, API, cloud sync, or RLS.
- **D-002:** SQLite schema separates task series from individual occurrences to preserve recurring-task history.
- **D-003:** App-open reminders are the initial baseline; closed-app reminders require separately tested Windows scheduling integration.
- **D-004:** Database belongs in `%LOCALAPPDATA%\\MyChecklist`, not beside the executable.
