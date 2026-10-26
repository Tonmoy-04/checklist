# MyChecklist — Context Architecture

This bundle contains the six specification documents and root instructions for Claude Code and Cursor. It is an architecture package, not the completed application source code.

## Contents

- `docs/01_PRD.md` — product goals, stories, acceptance criteria, non-goals
- `docs/02_AppFlow.md` — screens, actions, state transitions, error/empty states
- `docs/03_UI_Spec.md` — exact UI tokens, typography, spacing, component states
- `docs/04_TRD.md` — locked stack, architecture, dependencies, security, testing
- `docs/05_Schema.md` — relational SQLite schema, constraints, indexes, migration and backup rules
- `docs/06_Plan.md` — sequential implementation checklist and progress log
- `CLAUDE.md` — Claude Code context and workflow instructions
- `.cursorrules` — Cursor context and workflow instructions

## Use

1. Extract this folder into the root of your MyChecklist repository.
2. Open the repository root in Claude Code or Cursor.
3. Ask the agent to read the mandatory documents and begin only the next unchecked item in `docs/06_Plan.md`.
4. Review changes and test results after every item.
5. Keep `docs/06_Plan.md` updated as work progresses.

The current specification deliberately excludes authentication, remote APIs, cloud sync, and RLS because MyChecklist is a single-user local desktop application.
