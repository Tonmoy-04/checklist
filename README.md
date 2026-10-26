# MyChecklist

MyChecklist is a local-first Windows desktop task planner for personal,
academic, learning, health, and work tasks. It uses Python 3.12.x,
CustomTkinter, SQLite, and Plyer, with no server, account, cloud sync,
telemetry, or network requirement.

## Status

The application is being implemented incrementally according to
[`docs/06_Plan.md`](docs/06_Plan.md). The package and foundation configuration
and the Phase 3 task-list, statistics, settings, and reminder-polling
components are implemented. The package entry point and release packaging
remain planned work.

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

The application entry point will be exposed as implementation progresses:

```powershell
python -m mychecklist
```

At the current foundation stage, the entry-point module and UI have not yet
been implemented.

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

## Backup and restore

The planned backup flow uses SQLite's online backup API and stores backups in
the application-data backup directory. Restore will validate SQLite integrity
and the expected schema, create a pre-restore snapshot, require explicit
confirmation, and preserve the current database if restore fails.

Backup and restore are not implemented yet; do not treat copying a live
database file as a valid backup.

## Reminder limitation

Version 1 reminders are checked while MyChecklist is open. The application
does not claim to deliver reminders while closed. Closed-app reminders require
a separately implemented and tested Windows Task Scheduler integration.

## Architecture

The project follows the layered architecture specified in the technical
requirements:

```text
CustomTkinter UI -> application services -> repositories -> SQLite
```

See the six documents in [`docs/`](docs/) for the product, flow, UI, technical,
schema, and implementation-plan source of truth.
