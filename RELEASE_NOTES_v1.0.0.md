# MyChecklist v1.0.0 — First Release

MyChecklist is a local-first Windows desktop task planner for personal,
academic, learning, health, and work tasks.

## Download and install

Download `MyChecklist.exe` and `MyChecklist.exe.sha256` from the release assets.
This is a portable GUI executable, not an installer. Save it to a trusted
folder and launch it on Windows 10/11 64-bit.

Verify the executable with:

```powershell
Get-FileHash .\MyChecklist.exe -Algorithm SHA256
```

Compare the result with `MyChecklist.exe.sha256`.

On first launch, the app creates `%LOCALAPPDATA%\MyChecklist\` and stores the
SQLite database, logs, and backups there. It does not store mutable user data
beside the executable.

## Included functionality

- Task CRUD, completion/reopening, cancellation, and recurrence.
- Today, Upcoming, Overdue, All Tasks, and Completed views.
- Search, filters, sorting, statistics, and local settings.
- SQLite backup/restore with validation and pre-restore protection.
- In-app reminder polling while MyChecklist is open.

## Limitations

Closed-app reminders are not guaranteed. No installer or Windows scheduled-task
integration is included. Clean-account, display-scaling, packaged-GUI,
notification, and real-data backup/restore checks require manual verification
on the target Windows environment.
