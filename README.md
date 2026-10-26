# MyChecklist

MyChecklist is a local-first Windows desktop task planner for personal,
academic, learning, health, and work tasks. It uses Python 3.12.x,
CustomTkinter, SQLite, and Plyer, with no server, account, cloud sync,
telemetry, or network requirement.

## Version and status

MyChecklist v1.0.0 is a local-first Windows desktop task planner. The
implemented release includes task CRUD, recurring occurrences, task views and
filters, completion history, statistics, in-app reminder polling, local
settings, and SQLite backup/restore.

The release is a portable Windows executable, not an installer. Download
`MyChecklist.exe` from the GitHub release assets, save it to a trusted folder,
and launch it. No server, account, cloud sync, telemetry, or network access is
required.

## Features

- Create, edit, complete, reopen, and cancel tasks.
- Today, Upcoming, Overdue, All Tasks, and Completed views.
- Search, category/priority filters, and sorting.
- Daily, weekly, and monthly recurrence with preserved occurrence history.
- Statistics for daily progress, completion rate, and historical breakdowns.
- Local reminders while the application is open.
- Local theme/reminder settings and validated SQLite backup/restore.
- AppData storage outside the executable directory.

There is no bundled screenshot because a checked-in, genuine product screenshot
is not currently available. Do not infer GUI appearance from the executable
without running it.

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

## First launch

On first launch, MyChecklist creates its database, built-in categories, default
settings, logs, and backup directory under `%LOCALAPPDATA%\MyChecklist\`.
Existing data is opened in place on later launches and upgrades. Keep a
verified backup before installing an upgrade.

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

## Release checks and known limitations

The release executable was built on Windows 11 with Python 3.12.10 and
PyInstaller 6.11.1. Automated tests pass, but the following require manual
verification on the target machine:

- Packaged GUI launch on a clean Windows account.
- Window resizing at 850x580 and larger.
- 100%, 125%, and 150% display scaling.
- Desktop notification behavior.
- Backup and restore using a copy of real user data.
- Clean shutdown while reminder polling is active.

Reminders are not guaranteed while the app is closed. No Windows scheduled
task or installer is included in v1.0.0.

## Troubleshooting

If startup fails, close the app and preserve
`%LOCALAPPDATA%\MyChecklist\logs\app.log` and the database path when reporting
the problem. Do not delete the database to troubleshoot. If the database is
locked or corrupt, make a copy first and use a validated backup/restore path.
An unsupported future schema version stops startup without rewriting the file.

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

## Contributing

Create a Python 3.12 virtual environment, install the development dependencies,
run the full test suite, and preserve the layered UI/service/repository
architecture. See [`docs/04_TRD.md`](docs/04_TRD.md) and
[`docs/06_Plan.md`](docs/06_Plan.md) before making changes.

## License

No license has been selected for this repository. Until the project owner adds
a license, the repository should not be treated as open-source software.
