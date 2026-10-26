# 05 — Database Schema

## 1. Scope and identity model

MyChecklist is a single-user, local-first desktop app. There is no login, user table, remote database, server-side authorization, or Row-Level Security (RLS). Windows file-system permissions protect the local application-data directory. Application-level validation and SQLite constraints protect data integrity.

SQLite type affinity is used. Store dates as ISO text (`YYYY-MM-DD`), times as `HH:MM`, and event timestamps as UTC ISO-8601 text ending in `Z`. Convert timestamps to local time for display.

## 2. Entity relationship overview

```text
categories 1 ─── * task_series 1 ─── * task_occurrences
settings (key/value)
reminder_deliveries * ─── 1 task_occurrences
```

- `task_series` stores the reusable task definition and recurrence policy.
- `task_occurrences` stores individual scheduled instances, including completed history.
- A non-recurring task is represented by a series with recurrence `none` and one occurrence.
- `reminder_deliveries` deduplicates notification attempts per occurrence and reminder offset.
- `categories` contains built-in categories and user-created categories.
- `settings` stores local preferences.

## 3. Tables

### `categories`

| Column | SQLite type | Constraints / meaning |
|---|---|---|
| `id` | INTEGER | Primary key |
| `name` | TEXT | NOT NULL, UNIQUE, trimmed, max 50 chars |
| `is_builtin` | INTEGER | NOT NULL, CHECK in (0,1) |
| `is_archived` | INTEGER | NOT NULL DEFAULT 0, CHECK in (0,1) |
| `created_at` | TEXT | NOT NULL UTC ISO-8601 timestamp |

Built-in categories initially: Personal, University, Learning, Work, Health, Other. Category names are case-insensitively unique in application validation; enforce `UNIQUE(name COLLATE NOCASE)` in SQLite.

### `task_series`

| Column | SQLite type | Constraints / meaning |
|---|---|---|
| `id` | INTEGER | Primary key |
| `title` | TEXT | NOT NULL, length 1–200 after trim |
| `category_id` | INTEGER | NOT NULL FK -> `categories.id` |
| `priority` | TEXT | NOT NULL CHECK in `low`, `medium`, `high` |
| `recurrence` | TEXT | NOT NULL CHECK in `none`, `daily`, `weekly`, `monthly` |
| `interval_count` | INTEGER | NOT NULL DEFAULT 1, CHECK >= 1; v1 UI uses 1 |
| `start_date` | TEXT | NOT NULL ISO date |
| `due_time` | TEXT | NULL or valid `HH:MM` validated by service |
| `is_active` | INTEGER | NOT NULL DEFAULT 1, CHECK in (0,1) |
| `created_at` | TEXT | NOT NULL UTC timestamp |
| `updated_at` | TEXT | NOT NULL UTC timestamp |

Deleting a series must not cascade-delete completed history. Series deletion is implemented as a soft stop (`is_active=0`) plus explicit handling of future incomplete occurrences. A separate “delete all history” capability is out of scope.

### `task_occurrences`

| Column | SQLite type | Constraints / meaning |
|---|---|---|
| `id` | INTEGER | Primary key |
| `series_id` | INTEGER | NOT NULL FK -> `task_series.id` ON DELETE RESTRICT |
| `due_date` | TEXT | NOT NULL ISO date |
| `due_time` | TEXT | NULL or valid `HH:MM` |
| `status` | TEXT | NOT NULL CHECK in `open`, `completed`, `cancelled` |
| `completed_at` | TEXT | NULL or UTC timestamp |
| `created_at` | TEXT | NOT NULL UTC timestamp |
| `updated_at` | TEXT | NOT NULL UTC timestamp |
| `is_skipped` | INTEGER | NOT NULL DEFAULT 0, CHECK in (0,1) |

Constraints:
- `CHECK ((status = 'completed' AND completed_at IS NOT NULL) OR (status <> 'completed' AND completed_at IS NULL))` if reopen semantics clear `completed_at`.
- `UNIQUE(series_id, due_date, due_time)` to prevent duplicate occurrences. SQLite treats NULL values as distinct, so use a normalized non-null `due_time_key` or an expression index to prevent duplicates for all-day tasks.
- Completion and next-occurrence creation happen in one transaction.
- Completed occurrences remain immutable history except explicit reopen; reopen must be auditable through `updated_at` and state.

### `reminder_deliveries`

| Column | SQLite type | Constraints / meaning |
|---|---|---|
| `id` | INTEGER | Primary key |
| `occurrence_id` | INTEGER | NOT NULL FK -> `task_occurrences.id` ON DELETE CASCADE |
| `reminder_offset_minutes` | INTEGER | NOT NULL CHECK >= 0 |
| `scheduled_for` | TEXT | NOT NULL UTC timestamp |
| `attempted_at` | TEXT | NULL or UTC timestamp |
| `delivered_at` | TEXT | NULL or UTC timestamp |
| `status` | TEXT | NOT NULL CHECK in `pending`, `delivered`, `failed`, `dismissed` |
| `attempt_count` | INTEGER | NOT NULL DEFAULT 0 CHECK >= 0 |
| `last_error_code` | TEXT | NULL, short non-sensitive diagnostic |
| `created_at` | TEXT | NOT NULL UTC timestamp |

Constraints:
- `UNIQUE(occurrence_id, reminder_offset_minutes)` ensures at most one delivery record for a given reminder rule per occurrence.
- Delivery failure is recorded and retried only according to bounded retry policy.
- Do not store full exception tracebacks in this table.

### `settings`

| Column | SQLite type | Constraints / meaning |
|---|---|---|
| `key` | TEXT | Primary key |
| `value` | TEXT | NOT NULL |
| `updated_at` | TEXT | NOT NULL UTC timestamp |

Initial keys:
- `theme` = `dark`
- `reminders_enabled` = `true`
- `default_reminder_offset_minutes` = `0`
- `notify_missed_reminders` = `true`
- `schema_version` is managed by SQLite `PRAGMA user_version`, not this table.

## 4. Indexes

Required indexes:
- `idx_occurrences_due_status` on `task_occurrences(due_date, status)`
- `idx_occurrences_status_due` on `task_occurrences(status, due_date, due_time)`
- `idx_occurrences_series_date` on `task_occurrences(series_id, due_date)`
- `idx_reminder_status_schedule` on `reminder_deliveries(status, scheduled_for)`
- `idx_series_category_active` on `task_series(category_id, is_active)`
- Case-insensitive unique index on category name if not implemented as table constraint.
- A partial index for open occurrences may be added if query plans show benefit.

## 5. Integrity and migration rules

- `PRAGMA foreign_keys = ON` on every connection.
- `PRAGMA integrity_check` must return `ok` before restoring a backup.
- Apply migrations sequentially using `PRAGMA user_version` and a migration transaction.
- Do not drop columns/tables containing user data without an explicit migration and backup.
- Seed built-in categories idempotently; startup must not duplicate them.
- All task writes use repositories and transactions.
- Use a unique key or transactional existence check to make recurrence generation idempotent.
- Tests use a temporary database and verify foreign-key enforcement and uniqueness.

## 6. Backup/restore

- Backup via `sqlite3.Connection.backup()` to a user-selected `.db` file or default backups directory.
- Restore requires confirmation, integrity/schema checks, a pre-restore snapshot, and a clean connection shutdown.
- A failed restore must leave the current database usable.
- Never import a backup by executing SQL text from an external file; open and validate the SQLite database file.
