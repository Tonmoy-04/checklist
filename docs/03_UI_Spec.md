# 03 — UI Specification

## 1. Design direction

Modern, calm, dark-first desktop productivity UI. Use restrained accent color, clear typography, consistent spacing, and compact task cards. Avoid gradients, decorative animation, excessive borders, and color-only status communication.

## 2. Color tokens

All colors are exact design tokens. Do not scatter raw hex values through components; reference the central theme module.

### Dark theme (default)

| Token | Hex | Usage |
|---|---|---|
| `bg.canvas` | `#111318` | Main window background |
| `bg.sidebar` | `#171A21` | Navigation sidebar |
| `bg.surface` | `#1B1F28` | Cards and dialogs |
| `bg.surface_hover` | `#242A35` | Hovered rows/buttons |
| `bg.input` | `#151922` | Input fields |
| `border.default` | `#2C3340` | Subtle outlines |
| `text.primary` | `#F3F5F8` | Primary text |
| `text.secondary` | `#A7B0BF` | Secondary metadata |
| `text.muted` | `#788395` | Placeholder/disabled text |
| `accent.primary` | `#6D8DFF` | Primary action and focus |
| `accent.hover` | `#829DFF` | Hover primary action |
| `accent.pressed` | `#5577EA` | Pressed primary action |
| `status.success` | `#43B581` | Completed/success |
| `status.warning` | `#F0B44D` | Due soon/warning |
| `status.danger` | `#F16C75` | Overdue/destructive |
| `status.info` | `#63B3ED` | Informational |
| `priority.low` | `#63B3ED` | Low priority |
| `priority.medium` | `#F0B44D` | Medium priority |
| `priority.high` | `#F16C75` | High priority |

### Light theme (optional follow-up; dark theme ships first)

| Token | Hex |
|---|---|
| `bg.canvas` | `#F5F7FA` |
| `bg.sidebar` | `#FFFFFF` |
| `bg.surface` | `#FFFFFF` |
| `bg.surface_hover` | `#EDF1F7` |
| `bg.input` | `#F8FAFC` |
| `border.default` | `#D9E0EA` |
| `text.primary` | `#182230` |
| `text.secondary` | `#526173` |
| `text.muted` | `#7C8999` |
| `accent.primary` | `#4263D8` |
| `accent.hover` | `#3454C7` |
| `accent.pressed` | `#2946B4` |
| `status.success` | `#18794E` |
| `status.warning` | `#946200` |
| `status.danger` | `#C93643` |
| `status.info` | `#1769AA` |
| `priority.low` | `#1769AA` |
| `priority.medium` | `#946200` |
| `priority.high` | `#C93643` |

## 3. Typography

Use the Windows system font `Segoe UI` where available; use Tk's default fallback if unavailable.

| Style | Size | Weight | Usage |
|---|---:|---|---|
| `display` | 28 px | Bold | Main screen title |
| `heading` | 20 px | Semibold | Dialog/page section heading |
| `subheading` | 16 px | Semibold | Task title/card heading |
| `body` | 14 px | Normal | Standard labels and input text |
| `body_small` | 12 px | Normal | Category/date metadata |
| `caption` | 11 px | Normal | Helper text and secondary status |
| `button` | 13 px | Semibold | Button labels |

Do not use font size alone to convey priority or error state; combine text labels/icons with color.

## 4. Spacing, sizing, and layout

Use an 8 px base spacing scale; allowed half-step is 4 px.
- `space.1 = 4`
- `space.2 = 8`
- `space.3 = 12`
- `space.4 = 16`
- `space.5 = 24`
- `space.6 = 32`
- `space.7 = 40`

Rules:
- Default window: 1100 × 720 px; minimum 850 × 580 px.
- Sidebar: 210 px target width, fixed width at MVP.
- Main content horizontal padding: 24 px.
- Task row/card minimum height: 64 px.
- Input/button height: 36 px minimum.
- Modal width: 440–560 px, centered relative to parent.
- Corner radius: 8 px for controls, 12 px for cards, 14 px for major panels.
- Keep list content scrollable; never clip primary actions at minimum supported window size.

## 5. Core component states

### Button
- Default: accent fill for primary, surface/outline for secondary.
- Hover: use corresponding hover token.
- Pressed: use pressed token.
- Disabled: muted text and surface; no hover affordance.
- Focus: visible 2 px accent outline or equivalent keyboard focus ring.
- Destructive: danger text/fill; require confirmation for deletion.

### Input
- Default: input background, 1 px border.
- Focus: accent border/ring.
- Invalid: danger border plus inline text; do not rely on border color alone.
- Disabled: muted background/text.
- Placeholder uses muted token and is never a substitute for a field label.

### Checkbox
- Unchecked: clear outline.
- Checked: accent or success fill and visible check mark.
- Hover/focus: distinct border/ring.
- Completed task title may be struck through, but remains readable.

### Task card
- Default: surface background, subtle border.
- Hover: surface-hover background.
- Overdue: danger icon/label plus explicit “Overdue” text.
- Due soon: warning icon/label plus explicit due time.
- Completed: subdued metadata and completion timestamp; do not hide history.
- Priority: visible text label plus colored indicator.

### Dialog
- Modal backdrop and clear title.
- Save is primary; Cancel is secondary.
- Unsaved changes trigger a discard confirmation.
- Validation appears beside the relevant field.

### Empty/error/loading states
- Empty list: simple icon, one sentence, one clear next action.
- Empty search: say no results match current filters and provide Clear filters.
- Recoverable error: concise message and Retry where appropriate.
- Destructive/recovery error: state whether data was changed; never claim success without confirmation.
- Loading: only use for operations that take noticeable time; SQLite list queries should normally feel immediate.

## 6. Accessibility and interaction

- Keyboard navigation for all essential actions.
- Visible focus states.
- Text labels for priority and task status; no color-only meaning.
- Dialog errors are announced/focused where practical.
- Respect Windows display scaling; test 100%, 125%, and 150%.
- Avoid hover-only actions; edit/delete controls remain discoverable.
- Avoid unnecessary animation and flashing.

## 7. Visual acceptance checklist

- Dark theme matches tokens consistently.
- Main list, forms, dialogs, and sidebar use consistent spacing.
- Task cards remain legible at 850 × 580.
- Long titles wrap or truncate without hiding controls; full title remains accessible.
- Overdue, due-soon, high-priority, completed, and disabled states are visually distinct.
- Empty and error states have helpful copy.
