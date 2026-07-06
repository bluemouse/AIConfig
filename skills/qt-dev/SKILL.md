---
name: qt-dev
description: Write, review, debug, and explain Qt 6 desktop C++ applications with Widgets/Designer UI and CMake builds for graphics tools that host Vulkan or Metal renderers. Use when working on QApplication, QMainWindow, QAction, layouts, docks, .ui files, qt_add_executable, qt_standard_project_setup, QVulkanWindow, QVulkanInstance, QWidget::createWindowContainer, QRhiWidget, Qt Test, QSignalSpy, qt-cmake, or embedding render viewports in a Linux/Windows/macOS desktop app — even if the user says "Qt help" without naming Widgets. Qt 6 only, CMake only, Widgets only (no QML/Qt Quick).
---

# Qt Dev

Resolve `<SKILL_ROOT>` as the directory containing **this** skill's `SKILL.md`. Resolve
paths to `references/` and `scripts/` from that directory.

Write and review Qt 6 Widgets/CMake desktop code for applications where Qt provides the UI/UX
shell around a separate Vulkan or Metal renderer. Read bundled references on demand — do not
load all reference files unless the task requires them.

## When to Use

- Creating, reviewing, debugging, or explaining Qt 6 C++ Widgets/Designer desktop code
- Setting up or fixing Qt 6 CMake projects (`find_package(Qt6 ...)`, `qt_add_executable`,
  AUTOMOC/AUTOUIC, CTest/Qt Test)
- Building main windows, menus, toolbars, docks, dialogs, model/view panels, and settings
- Integrating render viewports with `QVulkanWindow`, custom Vulkan `QWindow`,
  `QWidget::createWindowContainer()`, `QRhiWidget`, or native Metal adapters on macOS
- QObject ownership, signals/slots, threading boundaries, and UI-thread responsiveness
- Qt Test + `QSignalSpy` for models, controllers, and render-bridge logic

## When NOT to Use

- **QML/Qt Quick UI** — Widgets/Designer only; do not suggest QML
- **qmake or Qt 5** — CMake + Qt 6 only; do not generate `.pro` files or Qt 5 compatibility
- **Pure C++20 without Qt APIs** — use [cpp-coding](../cpp-coding/SKILL.md)
- **GoogleTest/GoogleMock-only test setups** — use [cpp-testing](../cpp-testing/SKILL.md)
- **Vulkan device/memory/barriers/pipelines inside the engine** — use [vulkan-dev](../vulkan-dev/SKILL.md)
- **Render graph, bindless, GPU-driven architecture** — use [gpu-rendering-guide](../gpu-rendering-guide/SKILL.md)

## Operating model

Optimize for correctness first, then maintainability, then performance. Use the project's
existing CMake layout, Qt module links, C++ standard, and test targets as the source of truth.

Before editing or generating nontrivial code:

1. Inspect `CMakeLists.txt`, target links, `.ui` files, and test targets when available.
2. Confirm Qt 6 + CMake + Widgets scope. Replace qmake, Qt 5 macros, or QML with Qt 6
   Widgets/CMake equivalents and call out the migration.
3. Separate UI shell, render bridge, and engine ownership. Keep renderer headers free of
   `QWidget` when possible.
4. After changes, run the smallest meaningful verification first, then broaden: build, CTest,
   renderer validation when graphics code changed.

Non-negotiable constraints:

- CMake only: `find_package(Qt6 REQUIRED COMPONENTS ...)`, `qt_standard_project_setup()`,
  `qt_add_executable()`, target-based linking, CTest for tests.
- Qt idioms: QObject parent ownership, RAII for native graphics handles, function-pointer
  connects, queued cross-thread communication, explicit failure paths.
- UI thread must not block on I/O, shader compilation, asset loading, or GPU waits.

## Qt rules to enforce

Default to these rules unless project conventions contradict them:

- Qt 6 + CMake + Widgets only; reject qmake, QML, and Qt 5 compatibility paths.
- `QApplication` for widget apps; `QGuiApplication` only when there are no widgets.
- QObject parent ownership for QObject trees; RAII for native graphics handles.
- Function-pointer `connect()`; `Qt::QueuedConnection` across threads.
- No manual edits to generated `ui_*.h`; behavior lives in C++ wrapper classes.
- High-DPI viewports: physical size = logical size × `devicePixelRatio()`.
- One primary render viewport per window when using `createWindowContainer()`.
- See [api-framework.md](references/api-framework.md) for module/API choices and
  [best-practices.md](references/best-practices.md) for ownership, threading, and UI/UX.

## Cross-cutting principles

These themes apply to every Qt change:

1. **Scope enforcement** — Qt 6, CMake, Widgets; reject qmake, QML, and Qt 5 patterns
2. **Ownership clarity** — document who owns QWidget, QWindow, surfaces, and GPU handles
3. **GUI-thread safety** — widgets and models on the GUI thread; workers via queued signals
4. **Buildable slices** — every code answer includes CMake links and compile-ready snippets
5. **Verify before claiming** — run build/CTest or state what was not verified

## Workflow

### 1. Assess

- Identify task type: API explanation, project setup, code generation, review, debugging, or
  architecture guidance.
- Read every matching row in [Reference routing](#reference-routing) before editing.
- For rendering tasks, pick one integration path from
  [rendering-vulkan-metal.md](references/rendering-vulkan-metal.md#2-integration-decision-tree):
  `QVulkanWindow`, custom Vulkan `QWindow`, `createWindowContainer()`, `QRhiWidget`, or native
  Metal adapter — then make ownership explicit.

### 2. Implement

- Provide a minimal buildable slice: CMake target, source/header/ui files, test target when
  relevant, and exact configure/build/test commands.
- Follow the incremental loop in
  [workflow-testing-debugging.md](references/workflow-testing-debugging.md#2-implementation-workflow).
- Apply [api-framework.md](references/api-framework.md) for API and module choices.
- Apply [toolchain-cmake.md](references/toolchain-cmake.md) for CMake, moc/uic/rcc, and commands.
- Apply [best-practices.md](references/best-practices.md) for ownership, threading, UI/UX, and
  anti-patterns.

### 3. Verify

- Run build and CTest after each slice when a terminal is available.
- Complete the quality bar in
  [toolchain-cmake.md](references/toolchain-cmake.md#7-ci-and-quality-gates) and the completion
  checklist in
  [workflow-testing-debugging.md](references/workflow-testing-debugging.md#6-completion-checklist).
- For reviews, report findings by category: correctness, ownership/lifecycle, threading, API
  misuse, UI/UX, rendering integration, performance, build/test. Cite files/lines when available.
- For debugging, start with Qt logs (`QT_LOGGING_RULES`, `qt.vulkan`, `qt.rhi.general`), then
  Vulkan validation or Metal frame capture. Ask for logs only when missing data blocks progress.

## Tool usage expectations

When a terminal or code execution tool is available:

```bash
qt-cmake -S . -B build/debug -G Ninja -DCMAKE_BUILD_TYPE=Debug
cmake --build build/debug --parallel
ctest --test-dir build/debug --output-on-failure
```

If command planning would help, run or inspect
`<SKILL_ROOT>/scripts/qt_cmake_plan.py`:

```bash
python <SKILL_ROOT>/scripts/qt_cmake_plan.py --name render-tool --mode widgets --tests
python <SKILL_ROOT>/scripts/qt_cmake_plan.py --name render-tool --mode vulkan-window --tests
python <SKILL_ROOT>/scripts/qt_cmake_plan.py --name render-tool --mode rhi-widget --tests
```

## Reference routing

| Task | Read |
|------|------|
| Qt Core/Gui/Widgets APIs, object model, event loop, widgets, Designer, model/view, render-surface APIs | [api-framework.md](references/api-framework.md) |
| CMake, qt-cmake, moc/uic/rcc, resources, tests, deployment, platform build notes | [toolchain-cmake.md](references/toolchain-cmake.md) |
| QVulkanWindow, QWindow+QVulkanInstance, createWindowContainer, QRhiWidget, Metal adapter, viewport architecture | [rendering-vulkan-metal.md](references/rendering-vulkan-metal.md) |
| Planning, implementation loop, Qt Test strategy, debugging, review workflow, completion checklist | [workflow-testing-debugging.md](references/workflow-testing-debugging.md) |
| Ownership, threading, UI/UX, model/view, logging, performance, rendering integration, anti-patterns, review checklist | [best-practices.md](references/best-practices.md) |

When a change spans multiple areas, read **every matching row** — viewport integration needs
[rendering-vulkan-metal.md](references/rendering-vulkan-metal.md) and
[api-framework.md](references/api-framework.md); build failures need
[toolchain-cmake.md](references/toolchain-cmake.md).

## Quick completion checklist

Complete **both** before marking Qt work done:

1. **Code quality** — review checklist in
   [best-practices.md](references/best-practices.md#11-style-and-review-checklist) and
   [workflow-testing-debugging.md](references/workflow-testing-debugging.md#5-review-workflow)
2. **Build and verification** — follow
   [toolchain-cmake.md](references/toolchain-cmake.md#7-ci-and-quality-gates) and
   [workflow-testing-debugging.md](references/workflow-testing-debugging.md#6-completion-checklist):
   - `cmake --build build/debug --parallel`
   - `ctest --test-dir build/debug --output-on-failure`
   - renderer validation/capture when graphics integration changed

The Verify workflow step is satisfied only when checklist part 2 ran or unverified areas are
explicitly stated.

## Output standards

For code answers:

- Prefer small, compiling examples over long fragments.
- Include `#include`s and CMake target links for every Qt class used.
- Use `QApplication` for widget apps; `QGuiApplication` only when there are no widgets.
- Put `Q_OBJECT` classes in headers or ensure AUTOMOC can see them.
- Do not edit generated `ui_*.h`; edit `.ui` files or wrapper classes.
- Account for high-DPI: framebuffer size = logical size × `devicePixelRatio()`.
- Document native Vulkan/Metal handle ownership at every Qt boundary.
- Include tests or test guidance for behavior changes.

For reviews:

- Prioritize correctness, ownership/lifecycle, threading, rendering integration, and test gaps.
- Distinguish confirmed defects from style preferences.
- Provide concrete fixes and the command that would catch the issue next time.

## Resources

- [api-framework.md](references/api-framework.md) — Qt 6 API framework and module map
- [toolchain-cmake.md](references/toolchain-cmake.md) — CMake and build toolchain
- [rendering-vulkan-metal.md](references/rendering-vulkan-metal.md) — Vulkan/Metal viewport integration
- [workflow-testing-debugging.md](references/workflow-testing-debugging.md) — Engineering workflow
- [best-practices.md](references/best-practices.md) — Idiomatic Qt C++ design and review standards
- [SOURCES.md](SOURCES.md) — Provenance (read for attribution only)

Companion skills: [cpp-coding](../cpp-coding/SKILL.md), [cpp-testing](../cpp-testing/SKILL.md),
[vulkan-dev](../vulkan-dev/SKILL.md), [gpu-rendering-guide](../gpu-rendering-guide/SKILL.md)

External reference: [Build with CMake](https://doc.qt.io/qt-6/cmake-manual.html)
