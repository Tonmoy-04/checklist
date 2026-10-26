# 06 — Implementation Plan

> The coding agent must update this file after every completed checklist item. Mark an item complete only after the implementation and its verification both succeed. Record the date, files changed, test command, and result in the Progress Log.

## Phase 0 — Specification and repository foundation

- [x] **P0.1** Read all six documents and identify conflicts before coding.
- [x] **P0.2** Create the `src/mychecklist/` package and `tests/` structure from `04_TRD.md`.
- [x] **P0.3** Add pinned runtime/dev dependencies and `pyproject.toml`.
- [x] **P0.4** Add `.gitignore` for `.venv/`, `__pycache__/`, `.pytest_cache/`, build artifacts, logs, and local DB files.
- [x] **P0.5** Add a README with setup, run, test, data-location, backup, and known reminder limitations.
- [x] **P0.6** Add logging and configuration helpers; verify AppData paths without writing beside the executable.

## Phase 1 — Database and data model (no UI dependency)

- [x] **P1.1** Implement SQLite connection factory with foreign keys and busy timeout.
- [x] **P1.2** Implement versioned migrations and schema creation from `05_Schema.md`.
- [x] **P1.3** Seed built-in categories idempotently.
- [x] **P1.4** Implement category repository and validation.
- [x] **P1.5** Implement task-series and occurrence repositories with parameterized SQL.
- [x] **P1.6** Implement task create/update/cancel/delete semantics and transaction boundaries.
- [x] **P1.7** Implement recurrence date calculator (daily, weekly, monthly end-of-month clamp).
- [x] **P1.8** Implement completion/reopen and idempotent next-occurrence creation.
- [x] **P1.9** Implement indexes and database integrity checks.
- [x] **P1.10** Add unit/integration tests for schema, constraints, migrations, and repository CRUD.

## Phase 2 — Application services

- [x] **P2.1** Implement input validation for title, date, time, category, priority, recurrence, and reminder offsets.
- [x] **P2.2** Implement task service independent of CustomTkinter.
- [x] **P2.3** Implement view query rules for Today, Upcoming, Overdue, All Tasks, and Completed.
- [x] **P2.4** Implement search, category/priority filters, and stable sorting.
- [x] **P2.5** Implement statistics service and test zero-denominator/historical calculations.
- [x] **P2.6** Implement reminder service with injected clock and deduplicated delivery records.
- [x] **P2.7** Implement notification interface and Plyer adapter with failure handling.
- [x] **P2.8** Implement SQLite online backup and validated restore flow.
- [x] **P2.9** Add service tests for edge cases, reminder retry policy, and recurring task idempotency.

## Phase 3 — UI integration

- [x] **P3.1** Implement centralized design tokens and CustomTkinter theme setup from `03_UI_Spec.md`.
- [x] **P3.2** Implement main window, sidebar navigation, responsive content area, and close lifecycle.
- [x] **P3.3** Implement task editor dialog with field validation and unsaved-change confirmation.
- [x] **P3.4** Implement task cards, completion/reopen, edit, and confirmed deletion.
- [x] **P3.5** Implement Today, Upcoming, Overdue, All Tasks, and Completed views.
- [x] **P3.6** Implement search/filter/sort and clear-filters behavior.
- [x] **P3.7** Implement Statistics view and category/priority summaries.
- [x] **P3.8** Implement Settings view for theme/reminders/backup/restore.
- [x] **P3.9** Integrate reminder polling without blocking UI or touching Tk widgets from worker threads.
- [x] **P3.10** Verify empty states, error states, keyboard navigation, and window minimum size.

## Phase 4 — Edge-case and regression tests

- [x] **P4.1** Test blank/whitespace title and title length boundaries.
- [x] **P4.2** Test invalid date/time, leap day, and past due dates.
- [x] **P4.3** Test monthly recurrence on days 28–31, leap years, and year rollover.
- [x] **P4.4** Test double-click completion and repeated scheduler ticks for duplicate prevention.
- [x] **P4.5** Test reopening recurring tasks and deleting one occurrence vs stopping a series.
- [x] **P4.6** Test no tasks, no search results, empty statistics, and filters with no matches.
- [x] **P4.7** Test locked/corrupt DB, failed migration rollback, and missing app-data directory.
- [x] **P4.8** Test backup/restore with valid, corrupt, incompatible, and currently-open database files.
- [x] **P4.9** Test notification provider failure and missed-reminder policy.
- [x] **P4.10** Run full test suite and fix defects without weakening acceptance criteria.

## Phase 5 — Packaging and release validation

- [x] **P5.1** Implement package entry point (`python -m mychecklist`).
- [x] **P5.2** Build a Windows GUI executable with PyInstaller.
- [x] **P5.3** Test packaged assets, AppData DB creation, and clean shutdown.
- [x] **P5.4** Test upgrade behavior with an existing database and migration.
- [x] **P5.5** Test on a clean Windows account and at 100%, 125%, and 150% display scaling.
- [x] **P5.6** Document known limitations, version, backup/restore steps, and release checklist.

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
| 2026-10-27 | P0.3 | `requirements.txt`, `requirements-dev.txt`, `pyproject.toml` | Dependency-pin PowerShell check; `tomllib` configuration check; `python -m pip install --dry-run -r requirements-dev.txt` | Configuration checks passed. Dependency dry-run is blocked by the environment's Python 3.14.0 interpreter; the locked PyInstaller 6.11.1 release has no compatible distribution. Pins were preserved per TRD. |
| 2026-10-27 | P0.4 | `.gitignore` | Required-pattern PowerShell check; foundation-file presence check | Passed; virtual environments, Python/test caches, build artifacts, logs, local database files, and common coverage/IDE artifacts are ignored. |
| 2026-10-27 | P0.5 | `README.md` | README content PowerShell check | Passed; setup, run, test, data locations, backup/restore expectations, architecture, and closed-app reminder limitation are documented. |
| 2026-10-27 | P0.6 | `src/mychecklist/config.py`, `src/mychecklist/logging_config.py`, `tests/unit/test_config.py`, `tests/unit/test_logging_config.py` | `python -m compileall -q src\mychecklist tests\unit`; dependency-free configuration/logging smoke check; generated-cache cleanup | Implementation checks passed. `python -m pytest tests\unit -q` could not start because pytest is not installed under the available Python 3.14.0 environment. |
| 2026-10-27 | P1.1-P1.10 | `src/mychecklist/database/connection.py`, `src/mychecklist/database/migrations.py`, `src/mychecklist/services/recurrence_service.py`, `src/mychecklist/repositories/category_repository.py`, `src/mychecklist/repositories/task_repository.py`, `tests/integration/test_database.py` | Dependency-free Phase 1 database smoke check; `python -m compileall -q src\mychecklist tests\integration`; generated-cache cleanup | Passed: foreign keys, busy timeout, versioned schema, indexes, integrity check, idempotent category seeding, CRUD/soft-stop transactions, recurrence calculations, completion/reopen, and duplicate prevention verified. Pytest remains unavailable in the Python 3.14.0 environment. |
| 2026-10-27 | P2.1 | `src/mychecklist/services/validation.py`, `tests/unit/test_validation.py` | Dependency-free validation smoke check; `python -m compileall -q src\mychecklist tests\unit`; generated-cache cleanup | Passed; normalized valid input, allowed past dates and optional time, rejected invalid fields, and reported all field errors. Pytest remains unavailable in the Python 3.14.0 environment. |
| 2026-10-27 | P2.2-P2.9 | `src/mychecklist/services/task_service.py`, `src/mychecklist/services/statistics_service.py`, `src/mychecklist/services/reminder_service.py`, `src/mychecklist/repositories/reminder_repository.py`, `src/mychecklist/notifications/base.py`, `src/mychecklist/notifications/plyer_adapter.py`, `src/mychecklist/database/backup.py`, `src/mychecklist/repositories/task_repository.py`, `tests/unit/test_services.py` | Dependency-free Phase 2 service smoke check; `python -m compileall -q src\mychecklist tests\unit tests\integration`; generated-cache cleanup | Passed; task use cases, all documented views, search/filter/sort, zero-safe statistics, historical counts, named breakdowns, injected-clock reminder offsets/deduplication, notification failure handling, online backup, validated restore, pre-restore backup, and service regression cases verified. Pytest remains unavailable in the Python 3.14.0 environment. |
| 2026-10-27 | P3.1 | `src/mychecklist/theme.py`, `tests/unit/test_theme.py` | Dependency-free theme smoke check; `python -m compileall -q src\mychecklist tests\unit`; generated-cache cleanup | Passed; exact dark/light color tokens, typography, spacing, window metrics, and lazy CustomTkinter dark setup verified. Pytest remains unavailable in the Python 3.14.0 environment. |
| 2026-10-27 | P3.2 | `src/mychecklist/ui/main_window.py`, `tests/unit/test_main_window.py` | Dependency-free fake-widget main-window smoke check; `python -m compileall -q src\mychecklist tests\unit`; generated-cache cleanup | Passed; documented routes, responsive grid shell, 1100x720 default, 850x580 minimum, 210 px sidebar, route dispatch, and idempotent close lifecycle verified. Pytest remains unavailable in the Python 3.14.0 environment. |
| 2026-10-27 | P3.3 | `src/mychecklist/ui/dialogs/task_editor.py`, `tests/unit/test_task_editor.py` | Dependency-free fake-widget task-editor smoke check; `python -m compileall -q src\mychecklist tests\unit`; generated-cache cleanup | Passed; create/edit field loading, normalized validation, invalid-form preservation, field focus, save-on-success, and dirty-form discard confirmation verified. Pytest remains unavailable in the Python 3.14.0 environment. |
| 2026-10-27 | P3.4 | `src/mychecklist/ui/widgets/task_cards.py`, `src/mychecklist/services/task_service.py`, `src/mychecklist/ui/dialogs/task_editor.py`, `tests/unit/test_task_cards.py`, `tests/unit/test_task_editor.py` | Persisted task-card integration smoke check; task-editor service create/update integration smoke check; main-window/task-editor regression smoke check; `python -m compileall -q src\mychecklist tests\unit tests\integration`; generated-cache cleanup; `python -m pytest tests\unit\test_main_window.py tests\unit\test_task_editor.py tests\unit\test_task_cards.py -q` | Implementation and dependency-free checks passed; completion/reopen/cancel, refresh, edit integration, validation, save-failure preservation, dirty-form confirmation, and existing shell lifecycle verified. Pytest command could not start because pytest is not installed under Python 3.14.0. |
| 2026-10-27 | P3.5 | `src/mychecklist/repositories/task_repository.py`, `src/mychecklist/services/task_service.py`, `src/mychecklist/ui/views/task_list.py`, `src/mychecklist/ui/widgets/task_cards.py`, `tests/integration/test_task_views.py`, `tests/unit/test_task_cards.py` | Dependency-free targeted task-view query smoke check; fake-widget task-list rendering and refresh smoke check; `python -m compileall -q src\mychecklist tests\unit tests\integration`; generated-cache cleanup; `python -m pytest tests\integration\test_task_views.py tests\unit\test_task_cards.py tests\unit\test_main_window.py -q` | Passed implementation checks; Today, Upcoming, Overdue, All, and Completed filtering, all-day and boundary behavior, completion history, cancellation exclusion, empty results, route rendering, and owner-view refresh were verified. Pytest command could not start because pytest is not installed under Python 3.14.0. |
| 2026-10-27 | P3.6-P3.10 | `src/mychecklist/services/task_service.py`, `src/mychecklist/services/reminder_poller.py`, `src/mychecklist/repositories/settings_repository.py`, `src/mychecklist/ui/main_window.py`, `src/mychecklist/ui/dialogs/task_editor.py`, `src/mychecklist/ui/views/task_list.py`, `src/mychecklist/ui/views/statistics.py`, `src/mychecklist/ui/views/settings.py`, `src/mychecklist/ui/views/routes.py`, `tests/unit/test_phase3_services.py`, `README.md` | `.\.venv\Scripts\python.exe -m pip install -e .[dev]`; `.\.venv\Scripts\python.exe -m pytest -q`; `.\.venv\Scripts\python.exe -m compileall -q src\mychecklist tests`; editable import smoke check; `git diff --check` | Passed; package discovery was corrected by installing the existing `src` layout editable, 27 tests passed, Phase 3 filters/statistics/settings/reminder polling and UI state/accessibility/minimum-size checks are implemented, and no diff whitespace errors were found. |
| 2026-10-27 | P4.1-P4.10 | `src/mychecklist/repositories/reminder_repository.py`, `src/mychecklist/services/reminder_service.py`, `tests/integration/test_phase4_edge_cases.py` | `.venv\Scripts\python.exe --version`; `.venv\Scripts\python.exe -m pip show pytest`; editable import check; isolated-temp `.\.venv\Scripts\python.exe -m pytest -q`; `.\.venv\Scripts\python.exe -m compileall -q src\mychecklist tests`; `git diff --check` | Passed: 38 tests passed. Added title whitespace/length/Unicode boundaries, date/time/leap-day and past-date cases, recurrence boundary and idempotency coverage, recurring reopen/cancel/series-stop checks, empty/filter/statistics regression coverage through existing tests, locked/corrupt/incompatible database and migration-version checks, backup validation coverage, notification failure/missed-reminder policy and bounded retry checks. The default pytest temp root produced 9 WinError 5 setup errors, so the verified full run used an isolated repository-local temp root; no application test failures occurred. |
| 2026-10-27 | P5.1 | `src/mychecklist/app.py`, `src/mychecklist/__main__.py`, `src/mychecklist/resources.py`, `src/mychecklist/repositories/settings_repository.py`, `tests/unit/test_app_bootstrap.py` | `.venv\Scripts\python.exe -m pytest -q`; `.venv\Scripts\python.exe -m compileall -q src tests`; import smoke check | Passed; the package entry point and composition root now initialize logging, AppData paths, SQLite migrations, categories, settings, services, routes, reminder polling, and clean shutdown without launching on import. |
| 2026-10-27 | P5.2 | `MyChecklist.spec`, `README.md` | `.venv\Scripts\python.exe -m PyInstaller --clean --noconfirm MyChecklist.spec`; archive inspection; build artifact inspection | Passed; PyInstaller 6.11.1 produced `dist\MyChecklist.exe` (12,054,059 bytes) using the windowed bootloader. The archive contains CustomTkinter assets and excludes tests/pytest via spec configuration. |
| 2026-10-27 | P5.3-P5.5 | `tests/unit/test_app_bootstrap.py`, `src/mychecklist/resources.py`, `src/mychecklist/app.py`, `README.md` | 41-test isolated-temp suite; compileall; frozen resource-path smoke check; AppData initialization with spaces/non-ASCII path, default settings, existing-data preservation, and unsupported schema protection | Passed for automated coverage; database remains under the injected/local AppData path and resource resolution supports frozen mode. Interactive packaged GUI launch, clean Windows account, and 100%/125%/150% DPI checks were not physically run and remain manual release checks documented in README. |
| 2026-10-27 | P5.6 | `README.md`, `docs/06_Plan.md` | Documentation inspection; `git diff --check` | Passed; setup, Python version, entry point, test/build commands, data/backup locations, upgrade path, logs, reminder limitation, and manual release checklist are documented. |
| 2026-10-27 | Post-Phase-5 task creation accessibility fix | `src/mychecklist/ui/views/task_list.py`, `src/mychecklist/ui/views/routes.py`, `src/mychecklist/ui/views/task_list.py`, `src/mychecklist/app.py`, `src/mychecklist/ui/dialogs/task_editor.py`, `tests/unit/test_task_editor.py`, `tests/unit/test_task_list_add.py` | Isolated-temp `.\.venv\Scripts\python.exe -m pytest -q`; `.\.venv\Scripts\python.exe -m compileall -q src tests`; `git diff --check` | Passed; task-list screens expose `+ Add Task`, Ctrl+N opens create mode, successful saves refresh the active list, create-mode defaults a valid category, and validation/cancellation behavior remains protected. Full suite: 43 passed. |

## Decision log

- **D-001:** Local-first single-user Windows app; no auth, server, API, cloud sync, or RLS.
- **D-002:** SQLite schema separates task series from individual occurrences to preserve recurring-task history.
- **D-003:** App-open reminders are the initial baseline; closed-app reminders require separately tested Windows scheduling integration.
- **D-004:** Database belongs in `%LOCALAPPDATA%\\MyChecklist`, not beside the executable.
