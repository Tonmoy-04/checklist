# MyChecklist — Claude Code Project Rules

## Mandatory context loading

Before planning, editing, creating, deleting, or executing project code:
1. Read `docs/01_PRD.md`.
2. Read `docs/02_AppFlow.md`.
3. Read `docs/03_UI_Spec.md`.
4. Read `docs/04_TRD.md`.
5. Read `docs/05_Schema.md`.
6. Read `docs/06_Plan.md`.
7. Inspect the relevant existing source and tests before changing them.

Do not start implementation if these documents conflict. Explain the conflict and propose a minimal documented resolution first. The six docs are the product/architecture source of truth; this file defines agent workflow.

## Product and architecture invariants

- This is MyChecklist, a local-first Windows desktop task planner.
- Use Python 3.12.x, CustomTkinter, SQLite, and the pinned dependencies in `04_TRD.md`.
- No web server, REST API, authentication, cloud sync, telemetry, or RLS.
- Keep UI, services, repositories, database, and notification adapter separate.
- Store the production DB in `%LOCALAPPDATA%\\MyChecklist\\`.
- Never write the live database beside the executable.
- Use parameterized SQL, transactions, foreign-key enforcement, versioned migrations, and tested backups.
- Preserve recurring-task history; recurrence completion must be idempotent.
- Do not claim closed-app reminders work until they are implemented and verified.

## Required implementation workflow

1. Select the next unchecked atomic item from `docs/06_Plan.md`, respecting dependencies.
2. State the item ID and its acceptance criteria before coding.
3. Inspect relevant code and tests. Avoid broad unrelated rewrites.
4. Add or update tests before/alongside implementation; for behavior changes, test edge cases.
5. Implement only the selected item and necessary dependencies.
6. Run targeted tests, then the relevant broader test suite.
7. Inspect the diff for data-loss risks, unplanned dependencies, hard-coded paths, and violations of architecture.
8. Update `docs/06_Plan.md` immediately after each completed item:
   - mark `[x]` only if implementation and verification both pass;
   - add date, files changed, test command, and result to Progress Log;
   - if incomplete or blocked, leave unchecked and record the blocker.
9. Report what changed, commands/tests run, results, and remaining issues.

## Safety rules

- Never delete, overwrite, reset, or migrate user data without a safe and documented path.
- Never remove or weaken tests simply to make them pass.
- Never mark tests passed unless they were actually run and passed.
- Never silently change a locked dependency or schema decision.
- Never store secrets or task content in telemetry.
- Treat backup files as untrusted and validate them before restore.
- Do not add new product scope without updating the PRD, flow, TRD/schema as relevant, and plan.
- Do not mark an entire phase complete when only some checklist items are done.

## Code quality

- Use type hints for public service/repository interfaces where practical.
- Keep business logic testable without creating a GUI.
- Use standard-library logging; avoid `print()` in production code.
- Inject clocks into time-sensitive services to make tests deterministic.
- Catch exceptions at appropriate boundaries; do not hide failures with broad empty `except` blocks.
- Keep UI responsive and only access Tk widgets on the Tk main thread.
- Follow `docs/03_UI_Spec.md` for design tokens, sizing, and states.

## Completion response

At the end of each task, report:
- Plan item ID(s)
- Files changed
- Tests/commands executed and exact result
- `06_Plan.md` updates
- Known limitations or blocked follow-up work

Do not begin the next unrelated plan item until the current item is verified and the plan is updated, unless the user explicitly requests a broader batch.
