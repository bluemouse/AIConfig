# Qt Widgets Design and Implementation Patterns — non-obvious rules

Widget-selection tables (which control for which data type), layout basics, and
container semantics are baseline Qt knowledge — this file holds only the rules
implementations tend to get wrong. Target Qt 6; prefer the repository's Qt version
when it differs.

## Layouts and sizing

- Avoid fixed width/height unless the content has a real invariant; a top-level form
  gets a top-level layout; in a `QMainWindow`, content lives in `centralWidget` with
  its own layout.
- Size policies, size hints, stretch, and style metrics over fixed pixels; native style
  over style sheets — Qt Style Sheets are not browser CSS. When styling: scope
  selectors narrowly, test all widget states (hover/pressed/disabled/checked/focus),
  and avoid fixed dimensions that break font scaling.
- Use `QGroupBox` only when the group itself carries a meaningful label or enabled
  state — spacing often communicates grouping better than boxes.
- Do not make the whole application window a giant scrolling form when navigation
  or sections would be clearer.

## Dialogs and commands

- `QDialogButtonBox` adapts button ordering to the platform — never manually force
  Windows- or macOS-style order. Assign roles (accept/reject/apply/reset/destructive)
  rather than raw buttons.
- Share one `QAction` among menus, toolbars, context menus, and shortcuts so
  enabled/checked state and text stay synchronized; prefer
  `QKeySequence::StandardKey` — Qt maps standard keys to platform conventions.
- Show units next to numeric values (suffix properties) — never only in placeholder
  text. Validate near the field and explain predictable constraints before submission.

## Model/view

- Convenience item widgets (`QListWidget`/`QTreeWidget`/`QTableWidget`) only for
  small, local, simple data; use `QAbstractItemModel` subclasses, proxy models for
  filtering/sorting, and delegates for specialized presentation.
- Define selection behavior intentionally: single vs extended, row vs item, current
  vs selected, activation/Enter/Delete/drag-drop semantics.
- For large data, never build thousands of child widgets — model/view keeps UI
  state changes cheap and batchable.

## Desktop-tool layout

- Separate primary work area from supporting tools (navigation left, properties
  right, output bottom); persist user pane/dock customizations with
  `QMainWindow::saveState()`/`restoreState()` + `QSettings`.
- Do not hard-code one layout for long-session users when the workflow benefits
  from customization.

## State and feedback

- Do not disable controls without explaining why when the user is likely to need
  them; use status bars for low-priority transient info, never for actionable
  errors; represent dirty/unsaved state visibly with predictable Save behavior.
- Background work: measurable progress, otherwise a busy indicator; expose Cancel
  when safe; report errors near the affected workflow.

## `.ui` and C++ separation

- `.ui` holds stable structure (hierarchy, layouts, buddies, tab order, standard
  buttons); C++ holds behavior (model binding, validation, handlers, async,
  dynamic enable rules, persistence).
- Never edit generated `ui_*.h`; with CMake use AUTOUIC.

## Custom widgets

- Create one only when standard composition cannot express the interaction; it then
  must own focus policy and keyboard behavior, size hints/policy, all visual
  states, accessible role/name/events, high-DPI painting, and palette integration.
- Prefer widget promotion over a Designer plugin unless promotion is insufficient.

## Performance

- Never block the GUI thread with expensive work; keep rendering and UI feedback
  decoupled enough that the user sees progress and can cancel.
