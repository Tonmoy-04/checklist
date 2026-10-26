# 04 — Technical Requirements Document (TRD)

## 1. Architecture decisions (locked for v1)

- **Platform:** Windows 10/11 desktop.
- **Language/runtime:** CPython 3.12.x, 64-bit.
- **UI:** CustomTkinter 5.2.2 over Python's built-in Tkinter.
- **Database:** SQLite via Python standard-library `sqlite3`; no database server.
- **Notifications:** `plyer==2.1.0` adapter for desktop notifications; isolate behind a notification service so the provider can be replaced.
- **Tests:** `pytest==8.3.5`.
- **Packaging:** `pyinstaller==6.11.1` baseline; update pins only through an explicit dependency-change task and regression tests.
- **Date/time:** standard-library `datetime`, `zoneinfo` only if time-zone support is added later.
- **Network/API:** none. The application must not require internet access at runtime.
- **Persistence:** `%LOCALAPPDATA%\\MyChecklist\\checklist.db`.
- **App name:** `MyChecklist`.

The versions above are a reproducible baseline, not a claim that they are the latest releases. Keep direct dependencies pinned in `requirements.txt` and record Python version in setup documentation. Upgrade intentionally after compatibility tests.

## 2. Layered architecture

```text
Presentation (CustomTkinter views/dialogs)
        |
Application services (task use cases, validation, reminders, statistics)
        |
Repositories (parameterized SQL, transactions)
        |
SQLite database + versioned migrations
```

Rules:
- UI modules must not issue SQL directly.
- Repositories must not import CustomTkinter.
- Business logic must be testable without opening a window.
- Notification implementation is behind an interface.
- Reminder scheduling must not block the UI thread. Use `after()` for lightweight polling or a worker that communicates back to the UI safely; do not manipulate Tk widgets from a background thread.
- All database write operations are transactional.
- Use parameterized SQL; never concatenate user text into SQL.
- Use explicit schema migrations and a `PRAGMA user_version` or migrations table.
- Avoid global mutable state.

## 3. Required project structure

```text
MyChecklist/
├── CLAUDE.md
├── .cursorrules
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml
├── README.md
├── docs/
│   ├── 01_PRD.md
│   ├── 02_AppFlow.md
│   ├── 03_UI_Spec.md
│   ├── 04_TRD.md
│   ├── 05_Schema.md
│   └── 06_Plan.md
├── src/
│   └── mychecklist/
│       ├── __init__.py
│       ├── __main__.py
│       ├── app.py
│       ├── config.py
│       ├── theme.py
│       ├── ui/
│       │   ├── main_window.py
│       │   ├── views/
│       │   ├── dialogs/
│       │   └── widgets/
│       ├── services/
│       │   ├── task_service.py
│       │   ├── recurrence_service.py
│       │   ├── reminder_service.py
│       │   └── statistics_service.py
│       ├── repositories/
│       │   ├── task_repository.py
│       │   ├── settings_repository.py
│       │   └── reminder_repository.py
│       ├── database/
│       │   ├── connection.py
│       │   ├── migrations.py
│       │   └── backup.py
│       └── notifications/
│           ├── base.py
│           └── plyer_adapter.py
└── tests/
    ├── unit/
    ├── integration/
    └── ui/
```

Do not create every module as an empty stub up front. Create files when the corresponding plan item begins, while preserving the intended boundaries.

## 4. Dependencies

`requirements.txt` (runtime):
```text
customtkinter==5.2.2
plyer==2.1.0
```

`requirements-dev.txt`:
```text
-r requirements.txt
pytest==8.3.5
pyinstaller==6.11.1
```

Use Python's standard library for SQLite, date/time, logging, paths, and JSON. Avoid adding packages for features already supported by the standard library unless a documented need exists.

## 5. Database and file locations

- App data: `%LOCALAPPDATA%\\MyChecklist\\`
- Database: `%LOCALAPPDATA%\\MyChecklist\\checklist.db`
- Backups: `%LOCALAPPDATA%\\MyChecklist\\backups\\`
- Logs: `%LOCALAPPDATA%\\MyChecklist\\logs\\app.log`
- Never write mutable database files next to the installed `.exe` or into Program Files.
- Create directories with `pathlib.Path.mkdir(parents=True, exist_ok=True)`.
- Apply reasonable log rotation and never log full task content unless explicitly needed for debugging.

## 6. Reliability, concurrency, and migrations

- Enable `PRAGMA foreign_keys = ON` for every connection.
- Set a bounded SQLite busy timeout.
- Use WAL mode only if justified by concurrency and test it with backup/restore; otherwise use the default journal mode.
- Use one transaction for multi-step recurrence completion and reminder claiming.
- Use `sqlite3.Connection.backup()` for consistent backups.
- Before restore, close connections, validate the backup schema/version, preserve the current database as a timestamped pre-restore copy, then replace and reopen.
- Migrations must be versioned, transactional when SQLite permits, and tested against a copy of each supported prior schema.
- Never delete or silently overwrite a corrupt or incompatible database.

## 7. Reminder behavior

- v1 reminder polling occurs while the app is open.
- Default polling interval: 20 seconds (configurable constant).
- Reminder delivery records must be unique by occurrence and reminder rule.
- The notification adapter catches provider exceptions and returns a result object.
- A reminder is due when `now >= due_at - offset`; do not repeatedly notify after the first successful delivery.
- If the app starts after the due time, follow setting `notify_missed_reminders` (default true) and deliver at most one late notification for that occurrence.
- Do not guarantee closed-app reminders until a separate Windows Task Scheduler integration is implemented and tested.
- Never block the UI while sending notifications or scanning a large data set.

## 8. Security and privacy

- No authentication or RLS; single local user, local SQLite file.
- Store no passwords, tokens, or secrets.
- No telemetry, external requests, or task-content uploads.
- Use parameterized SQL and strict input validation.
- Treat imported backup files as untrusted: validate schema, database integrity (`PRAGMA integrity_check`), and expected application tables before restore.
- Avoid unsafe pickle deserialization and shell execution with user-controlled content.
- Error messages may be shown to users, but logs should avoid sensitive task text by default.
- File paths used for backup/restore must be validated and confirmation required before replacing current data.

## 9. Testing and quality gates

Commands:
```powershell
python -m pytest
python -m mychecklist
```

During development, launch from the repository root with the package installed editable (`python -m pip install -e .`) or use a documented equivalent.

Minimum quality gates:
- Unit tests for validation, recurrence date calculation, reminder due logic, and statistics.
- Repository integration tests use a temporary database, never the user's real database.
- Migration tests from empty database and each supported schema version.
- UI smoke test for startup, navigation, task CRUD, and graceful shutdown.
- Package smoke test on clean Windows user profile.
- Tests must not rely on the wall clock without an injected/frozen clock.
- Do not remove or weaken a test to make a change pass; update tests only when the product specification changes.

## 10. Packaging

- Build with PyInstaller only after module execution works from source.
- Use `--windowed` for GUI release builds.
- Include dependency data only when required; test CustomTkinter assets in the packaged executable.
- Verify database stays in AppData after install/update/uninstall.
- Keep a version number and release notes.
