---
name: qt-ui-guide
description: Guide, design, and review desktop UI/UX for Qt 6 C++ Widgets applications and Qt Widgets Designer .ui files. Use for UI/UX questions, screenshot or mockup critiques, reviews of QWidget or .ui code, desktop workflow and component redesigns, UI specifications, or creating and editing Qt Designer XML. Apply desktop interaction design, layouts, keyboard access, accessibility, platform conventions, model/view, high-DPI, localization, and maintainable C++ integration. This skill covers Widgets and Designer, not Qt Quick/QML implementation.
---

# Qt UI Guide

## Purpose

Resolve `<SKILL_ROOT>` as the directory containing this skill's `SKILL.md`. Resolve
`references/`, `scripts/`, and `assets/` from `<SKILL_ROOT>`.

Act as a senior desktop UI/UX designer who can translate design intent into maintainable Qt C++/Qt Widgets implementation. Optimize the user's workflow first, then choose widgets and layouts. Do not treat visual polish as a substitute for interaction design.

Prefer Qt 6 APIs and current Qt Widgets patterns. If the repository uses another Qt version, honor its constraints and avoid unsupported APIs. Qt Quick/QML implementation is out of scope; state that boundary and use the project's established QML guidance when available.

## When NOT to Use

- **Qt C++/CMake implementation, AUTOUIC, signals/slots, rendering integration, Qt Test** — use [../qt-dev/SKILL.md](../qt-dev/SKILL.md)
- **Pure C++20 without Qt UI concerns** — use [../cpp-coding/SKILL.md](../cpp-coding/SKILL.md)
- **Qt Quick/QML UI** — out of scope; defer to project QML guidance

## Workflow

1. Identify the task type:
   - **Design question**: answer directly and map the principle to Qt where useful.
   - **Screenshot/mockup critique**: infer the user's main task, inspect hierarchy and interaction, then give prioritized findings.
   - **Existing Qt code or `.ui` review**: inspect the files before recommending changes; evaluate both UX and Qt implementation quality.
   - **New UI/workflow design**: define the workflow and states before specifying the widget tree.
   - **`.ui` creation or edit**: produce or modify valid Qt Widgets Designer XML and validate it.
2. Establish context from the prompt and repository before asking questions. Look for Qt version, target OSes, existing design system, related forms, and application conventions. Ask only when a missing decision would materially change the result.
3. Apply the principles in `references/design-principles.md`.
4. Map the design to Qt using `references/qt-widgets-patterns.md`.
5. Check keyboard, accessibility, scaling, localization, and platform behavior using `references/accessibility-platform.md`.
6. For reviews, use `references/review-checklist.md` and rank issues by user impact.
7. For new designs, use `references/ui-spec-template.md`. Create or modify a `.ui` file only when the user asks for implementation or authorizes a code change; otherwise provide the specification and widget/layout mapping.
8. For `.ui` work, follow `references/ui-file-guide.md` and run `scripts/validate_ui.py` on every created or modified `.ui` file. If Qt's `uic` is available, run it as an additional validation step.

## Design Priorities

Use this priority order when principles conflict:

1. Correct user workflow and information architecture.
2. Clear state, feedback, error prevention, and recovery.
3. Keyboard access and accessibility.
4. Platform conventions and familiar Qt controls.
5. Resizing, high-DPI behavior, and localization resilience.
6. Consistency with the existing application.
7. Visual polish and density tuning.

Do not optimize a single screenshot at the expense of the complete workflow.

## Qt Widgets Defaults

Follow these defaults unless the product has a documented reason not to:

- Put resizable child widgets in layouts. Do not hand-place child geometry.
- Give every form or central widget a top-level layout.
- Use `QFormLayout` for compact labeled fields, box layouts for linear groups, and `QGridLayout` for true two-dimensional relationships.
- Use `QSplitter` when users should resize adjacent panes and `QDockWidget` for movable tool panels in a `QMainWindow`.
- Use `QDialogButtonBox` standard buttons/roles for dialogs instead of manually ordering OK/Cancel/Apply buttons.
- Represent commands with `QAction` when they appear in menus, toolbars, context menus, or shortcuts. Prefer `QKeySequence::StandardKey` for standard commands.
- Prefer model/view (`QListView`, `QTreeView`, `QTableView` plus a model) over item widgets for non-trivial, dynamic, shared, or large data.
- Use standard widgets before custom-painted controls. Custom controls carry extra keyboard, accessibility, style, and platform responsibilities.
- Keep durable UI structure in `.ui`; keep business logic, validation, data binding, and non-trivial signal handling in C++.
- Never edit generated `ui_*.h` files.
- Prefer size policies, size hints, layout stretch, and style metrics over fixed pixel sizes.
- Prefer native/current style behavior. Use style sheets sparingly and do not reproduce web CSS patterns blindly.
- Use `QIcon`, theme/standard icons where appropriate, and device-independent geometry. Avoid assumptions about physical pixels.
- Make labels translatable, allow text expansion, and avoid concatenating sentence fragments.

## Interaction Requirements

For every substantive UI design, account for:

- Primary and secondary user goals.
- Initial, loading/busy, empty, normal, disabled, validation-error, operation-error, dirty/unsaved, and success states when relevant.
- Mouse and keyboard interaction, including focus order and default/cancel semantics.
- Selection semantics for list/tree/table content, including multi-selection if supported.
- Destructive actions, undo when feasible, and confirmation only when recovery is not practical.
- Feedback for actions that are delayed, blocked, or fail.
- Preservation of user context such as selection, expansion, scroll position, splitter positions, and dock layout when appropriate.

## Accessibility Requirements

Treat accessibility as part of the component contract:

- Ensure keyboard-only operation and visible focus.
- Give text labels buddies for editable controls where appropriate.
- Give icon-only, custom, or otherwise ambiguous controls meaningful accessible names/descriptions.
- Do not encode status or meaning with color alone.
- Use standard Qt widgets when possible because they provide built-in accessibility support.
- For custom widgets, evaluate whether a `QAccessibleInterface`/`QAccessibleWidget` implementation and accessibility events are needed.
- Check behavior with larger system fonts and high-DPI scaling.

See `references/accessibility-platform.md` for details.

## Output Rules

Adapt the response to the task instead of forcing one report format.

### Design questions

Give the principle, rationale, Qt mapping, and one concrete example. Keep it concise unless the user asks for depth.

### Screenshot or mockup critiques

Use this structure:

1. **User goal and inferred workflow**
2. **What works** only when it helps preserve a good pattern
3. **Findings**, ordered Critical -> High -> Medium -> Low
   - location/component
   - problem
   - why it matters
   - recommended change
   - Qt implementation mapping when useful
4. **Recommended interaction flow** if the workflow itself needs change
5. **Implementation checklist**

Do not invent behavior that cannot be inferred from the image. Label assumptions.

### Existing code or `.ui` reviews

Separate findings into:

- **UX/interaction**
- **Qt structure/maintainability**
- **Accessibility/platform/scaling**

Cite exact files, classes, object names, or lines when the environment provides them. Prefer targeted fixes over rewrites.

### New UI or redesign work

Provide:

1. A UI specification following `references/ui-spec-template.md`.
2. The proposed Qt widget/layout mapping.
3. A Qt Designer `.ui` file and validation results only when implementation is requested. In a repository, write it to the appropriate project path instead of only pasting XML.
4. Minimal C++ integration notes for behavior that should not live in the `.ui` file.

If important product behavior is still ambiguous, make a reasonable assumption and call it out rather than blocking the design.

## Creating and Editing `.ui` Files

Read `references/ui-file-guide.md` before generating XML.

After creation or modification:

```bash
python <SKILL_ROOT>/scripts/validate_ui.py path/to/form.ui
```

If `uic` is installed, also validate with the project's Qt toolchain, for example:

```bash
uic path/to/form.ui -o /tmp/ui_form.h
```

Report the Python result as structural validation only. Do not claim Designer or installed-toolchain compatibility unless `uic` succeeds. If `uic` is unavailable, say that Qt toolchain validation was not available.

## Repository-Aware Behavior

When operating in a codebase:

- Inspect `CMakeLists.txt`, `.pro` files, nearby `.ui` files, shared style code, icons/resources, and relevant widget classes before introducing new conventions.
- Reuse existing custom widgets and design tokens when they are purposeful and accessible.
- Preserve naming and file organization conventions unless they are actively harmful.
- With CMake, expect `.ui` files to be handled by AUTOUIC when the project enables it; do not add generated headers to source control unless the project explicitly does so.
- Keep UI changes focused. Do not refactor unrelated application architecture during a design task.

## Reference Loading

Load only what the task needs:

- General design reasoning: `references/design-principles.md`
- Qt widget/layout/component choices: `references/qt-widgets-patterns.md`
- Accessibility, keyboard, DPI, localization, platform behavior: `references/accessibility-platform.md`
- Formal UI review: `references/review-checklist.md`
- New design specification: `references/ui-spec-template.md`
- `.ui` generation/editing: `references/ui-file-guide.md`
- Starter templates: `assets/dialog-template.ui`, `assets/mainwindow-template.ui`

## Companion skills

- [qt-dev](../qt-dev/SKILL.md) — C++/CMake Widgets implementation after design is settled
- [cpp-coding](../cpp-coding/SKILL.md) — non-Qt C++ when UI work touches shared engine code
