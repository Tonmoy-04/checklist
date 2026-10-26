# MyChecklist

MyChecklist is a local-first Windows desktop task planner for personal,
academic, learning, health, and work tasks. It uses Python 3.12.x,
CustomTkinter, SQLite, and Plyer, with no server, account, cloud sync,
telemetry, or network requirement.

## Status

The application is being implemented incrementally according to
[`docs/06_Plan.md`](docs/06_Plan.md). The package and foundation configuration
and the Phase 3 task-list, statistics, settings, reminder-polling components,
application entry point, and Windows packaging configuration are implemented.
Release validation still requires the manual Windows-account and DPI checks
listed below.

## Requirements

- Windows 10 or 11
- 64-bit CPython 3.12.x
- A virtual environment

Dependency pins are defined in [`requirements.txt`](requirements.txt) and
[`requirements-dev.txt`](requirements-dev.txt).

## Setup

From the repository root in PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
python -m pip install -e .
```

The project targets Python 3.12.x. The pinned PyInstaller release is part of
the reproducible Windows build baseline and may not resolve on newer Python
versions.

## Run

```powershell
python -m mychecklist
```

The command resolves the production database under `%LOCALAPPDATA%` and does
not create application data merely by importing `mychecklist`.

## Test

Run the complete available test suite from the repository root:

```powershell
python -m pytest
```

Tests use temporary directories and must never modify the production database.

## Data locations

The production database is stored at:

```text
%LOCALAPPDATA%\MyChecklist\checklist.db
```

Backups and logs are stored under:

```text
%LOCALAPPDATA%\MyChecklist\backups\
%LOCALAPPDATA%\MyChecklist\logs\app.log
```

The application never uses its executable directory as the mutable database
location. Data directories are created during application startup, not when
the configuration module is imported.

## Build the Windows executable

From the activated Python 3.12 environment:

```powershell
python -m pip install -e .[dev]
python -m PyInstaller --clean --noconfirm MyChecklist.spec
```

The release executable is written to `dist\MyChecklist.exe` by the one-file
spec configuration. Use `--console` only for a temporary diagnostic
build if startup logging needs to be observed.

## Backup and restore

The backup flow uses SQLite's online backup API and stores backups in the
application-data backup directory. Restore validates SQLite integrity and the
expected schema, creates a pre-restore snapshot, requires explicit
confirmation, and preserves the current database if validation fails. Do not
copy a live SQLite file while it is being written as a substitute for this
flow.

## Reminder limitation

Version 1 reminders are checked while MyChecklist is open. The application
does not claim to deliver reminders while closed. Closed-app reminders require
a separately implemented and tested Windows Task Scheduler integration.

## Upgrade and diagnostics

For an upgrade, close MyChecklist, install the new release, and launch it
against the existing `%LOCALAPPDATA%\MyChecklist\checklist.db`. Migrations
run transactionally before the UI is shown. Keep a verified backup before
upgrading. A future unsupported schema version stops startup without
rewriting the database.

Startup and reminder diagnostics are written to
`%LOCALAPPDATA%\MyChecklist\logs\app.log`. Preserve that file and the
database path when reporting a failure. The executable never stores mutable
database or log files in its installation directory or PyInstaller's
temporary extraction directory.

Before publishing a Windows release, manually verify:

1. A clean Windows account creates `%LOCALAPPDATA%\MyChecklist\` on first run.
2. Existing data remains available after installing an upgrade.
3. The GUI launches at 100%, 125%, and 150% display scaling.
4. The window remains usable at 850x580 and task-editor controls remain visible.
5. Backup and restore work with a copy of a real database.
6. Closing the app stops reminder polling and leaves no locked database handle.
7. Notifications behave as documented, including the closed-app limitation.

These account, DPI, and packaged-GUI checks are not claimed as automated
verification in this development environment.

## Architecture

The project follows the layered architecture specified in the technical
requirements:

```text
CustomTkinter UI -> application services -> repositories -> SQLite
```

See the six documents in [`docs/`](docs/) for the product, flow, UI, technical,
schema, and implementation-plan source of truth.
