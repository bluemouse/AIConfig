---
name: qt-ui-guide
description: Guide, design, and review desktop UI/UX for Qt 6 C++ Widgets applications and Qt Widgets Designer .ui files. Use for UI/UX questions, screenshot or mockup critiques, reviews of QWidget or .ui code, desktop workflow and component redesigns, UI specifications, or creating and editing Qt Designer XML. Apply desktop interaction design, layouts, keyboard access, accessibility, platform conventions, model/view, high-DPI, localization, and maintainable C++ integration. This skill covers Widgets and Designer, not Qt Quick/QML implementation.
---

# Qt UI Guide

## Purpose

Resolve `<SKILL_ROOT>` as the directory containing this skill's `SKILL.md`. Resolve
`references/`, `scripts/`, and `assets/` from `<SKILL_ROOT>`.

Act as a senior desktop UI/UX designer who can translate design intent into maintainable Qt C++/Qt Widgets implementation. Optimize the user's workflow first, then choose widgets and layouts. Prefer Qt 6 APIs; honor the repository's Qt version constraints. Qt Quick/QML implementation is out of scope; state that boundary and defer to the project's QML guidance when available.

## When NOT to Use

- **Qt C++/CMake implementation, AUTOUIC, signals/slots, rendering integration, Qt Test** — use [../qt-dev/SKILL.md](../qt-dev/SKILL.md)
- **Pure C++20 without Qt UI concerns** — use [../cpp-coding/SKILL.md](../cpp-coding/SKILL.md)
- **Qt Quick/QML UI** — out of scope; defer to project QML guidance

## Workflow

1. Identify the task type:
   - **Design question**: answer directly and map the principle to Qt where useful.
   - **Screenshot/mockup critique**: infer the main task, inspect hierarchy and interaction, then give prioritized findings.
   - **Code or `.ui` review**: inspect the files first; evaluate both UX and Qt implementation quality.
   - **New UI/workflow design**: define the workflow and states before specifying the widget tree.
   - **`.ui` creation or edit**: produce or modify valid Designer XML and validate it.
2. Establish context from the prompt and repository (Qt version, target OSes, design system, conventions) before asking questions; ask only when a missing decision would materially change the result.
3. Apply `references/design-principles.md`, then map the design to Qt with `references/qt-widgets-patterns.md`. Check keyboard, accessibility, scaling, localization, and platform behavior with `references/accessibility-platform.md`; rank review findings with the severity rubric in `references/design-principles.md`.
4. For new designs, use `references/ui-spec-template.md`. Create or modify a `.ui` file only when the user asks for implementation or authorizes a code change; otherwise provide the specification and widget/layout mapping.
5. For `.ui` work, follow `references/ui-file-guide.md` and run `scripts/validate_ui.py` on every created or modified `.ui` file. If Qt's `uic` is available, run it as an additional validation step.

Design priorities, interaction-state coverage, and accessibility are part of every substantive design: apply the priority order, state list, and severity rubric in `references/design-principles.md` and the accessibility requirements in `references/accessibility-platform.md`.

## Qt Widgets Defaults

Defaults for common cases; full patterns, control-choice tables, and official references in `references/qt-widgets-patterns.md`:

- Layouts for all resizable content — `QFormLayout` for labeled fields, box layouts for linear groups, `QGridLayout` for true two-dimensional relationships; never hand-place child geometry; every form or central widget gets a top-level layout.
- `QSplitter` for user-resizable adjacent panes; `QDockWidget` for movable tool panels; `QDialogButtonBox` for dialog buttons — never manually order OK/Cancel.
- `QAction` for commands appearing in menus, toolbars, context menus, or shortcuts; prefer `QKeySequence::StandardKey`.
- Model/view (`QListView`/`QTreeView`/`QTableView` plus a model) over item widgets for non-trivial, dynamic, shared, or large data.
- Standard widgets before custom-painted controls; custom controls carry extra keyboard, accessibility, style, and platform responsibilities.
- Durable UI structure in `.ui`; business logic, validation, data binding, and non-trivial signal handling in C++. Never edit generated `ui_*.h` files.
- Size policies, size hints, stretch, and style metrics over fixed pixels; native style over style sheets — do not reproduce web CSS patterns blindly.
- `QIcon`/theme icons and device-independent geometry; translatable labels with room for text expansion.

## Output Rules

Adapt the response to the task instead of forcing one report format. Order findings Critical -> High -> Medium -> Low using the rubric in `references/design-principles.md`. For code or `.ui` reviews, cite exact files, classes, object names, or lines, and prefer targeted fixes over rewrites.

Do not invent behavior that cannot be inferred from a screenshot or mockup. Label assumptions, and make a reasonable assumption for ambiguous product behavior rather than blocking the design.

## Creating and Editing `.ui` Files

Read `references/ui-file-guide.md` before generating XML. After creation or modification:

```bash
python <SKILL_ROOT>/scripts/validate_ui.py path/to/form.ui
```

If `uic` is installed, also validate with the project's Qt toolchain, for example `uic path/to/form.ui -o /tmp/ui_form.h`. Report the Python result as structural validation only. Do not claim Designer or installed-toolchain compatibility unless `uic` succeeds.

## Repository-Aware Behavior

- Inspect `CMakeLists.txt`, nearby `.ui` files, shared style code, and relevant widget classes before introducing new conventions. Reuse existing custom widgets and design tokens when purposeful and accessible; preserve naming and file organization unless actively harmful.
- With CMake, expect `.ui` files to be handled by AUTOUIC; do not add generated headers to source control unless the project does so. Keep UI changes focused — no unrelated refactoring.

## Reference Loading

Load only what the task needs:

- General design reasoning and review severity rubric: `references/design-principles.md`
- Qt widget/layout/component choices: `references/qt-widgets-patterns.md`
- Accessibility, keyboard, DPI, localization, platform behavior: `references/accessibility-platform.md`
- New design specification: `references/ui-spec-template.md`
- `.ui` generation/editing: `references/ui-file-guide.md`
- Starter templates: `assets/dialog-template.ui`, `assets/mainwindow-template.ui`

## Companion Skills

- [qt-dev](../qt-dev/SKILL.md) — C++/CMake Widgets implementation after design is settled
- [cpp-coding](../cpp-coding/SKILL.md) — non-Qt C++ when UI work touches shared engine code
