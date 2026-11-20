---
name: qt-dev
description: "Write, review, and debug Qt 6 C++ Widgets/CMake desktop applications hosting Vulkan or Metal renderers: `QApplication`, `QMainWindow`, layouts/docks, `.ui` integration, `qt_add_executable`, `QVulkanWindow`, `createWindowContainer`, `QRhiWidget`, and Qt Test (`QSignalSpy`) — Qt 6 + CMake + Widgets only (no QML/Qt Quick)."
---

# Qt Dev

Write and review Qt 6 Widgets/CMake desktop code where Qt provides the UI shell around a
separate Vulkan or Metal renderer. Resolve `<SKILL_ROOT>` as this skill's directory; read the
bundled references on demand — do not load all reference files unless the task requires them.

## When to Use

- Qt 6 C++ Widgets/Designer desktop code: creating, reviewing, debugging, or explaining
- Qt 6 CMake project setup (`find_package(Qt6 ...)`, `qt_add_executable`, AUTOMOC/AUTOUIC,
  CTest/Qt Test), render viewport integration, QObject ownership/signals/slots/threading,
  or Qt Test + `QSignalSpy`

## When NOT to Use

- **QML/Qt Quick UI** — Widgets/Designer only; do not suggest QML
- **qmake or Qt 5** — CMake + Qt 6 only; do not generate `.pro` files or Qt 5 compatibility
- **Pure C++20 without Qt APIs, or GoogleTest/GoogleMock-only test setups** — use
  [cpp-coding](../cpp-coding/SKILL.md)
- **Vulkan device/memory/barriers/pipelines inside the engine** — use [vulkan-dev](../vulkan-dev/SKILL.md)
- **Render graph, bindless, GPU-driven architecture** — use [gpu-rendering-guide](../gpu-rendering-guide/SKILL.md)
- **UI/UX design, mockup critique, workflow redesign, accessibility review, or `.ui` authoring** — use [qt-ui-guide](../qt-ui-guide/SKILL.md)

## Operating model

Correctness first, then maintainability, then performance. Treat the project's existing CMake
layout, Qt module links, C++ standard, and test targets as the source of truth — inspect them
before generating nontrivial code. Run the smallest meaningful verification first, then
broaden: build, CTest, renderer validation when graphics code changed.

## Rules

Default to these unless project conventions contradict them:

- Qt 6 + CMake + Widgets only; reject qmake, QML, and Qt 5 compatibility paths.
- QObject parent ownership for QObject trees; RAII for native graphics handles; document who
  owns every QWidget, QWindow, surface, and Vulkan/Metal handle at each Qt boundary.
- Function-pointer `connect()`; `Qt::QueuedConnection` across threads; widgets and models stay
  on the GUI thread with workers behind queued signals; the UI thread must not block on I/O,
  shader compilation, asset loading, or GPU waits.
- No manual edits to generated `ui_*.h`; behavior lives in C++ wrapper classes; keep
  `Q_OBJECT` classes in headers where AUTOMOC can see them.
- High-DPI viewports: framebuffer size = logical size × `devicePixelRatio()`.
- One primary render viewport per window when using `createWindowContainer()`.
- Every code answer is a minimal buildable slice: compiling snippet with `#include`s, CMake
  target links for every Qt class used, and tests or test guidance for behavior changes.
- Verify before claiming: run build/CTest, or state explicitly what was not verified.
- For module/API choices see [api-framework.md](references/api-framework.md); for ownership,
  threading, and UI/UX see [best-practices.md](references/best-practices.md).

## Renderer integration choice

Pick one path, make ownership explicit, and keep renderer headers free of `QWidget` when
possible (details in
[rendering-vulkan-metal.md](references/rendering-vulkan-metal.md#2-integration-decision-tree)):

1. `QVulkanWindow` — Qt owns device/queue/swapchain; prototypes, tools, simple examples.
2. Custom `QWindow` + `QVulkanInstance` — engine owns device/swapchain; Qt provides the
   window/surface.
3. `QWidget::createWindowContainer(QWindow*)` — `QWindow` viewport inside a Widgets UI; one
   primary viewport, no overlapping overlays.
4. `QRhiWidget` — Qt-managed widget-composited previews via Vulkan or Metal; accepts QRhi
   compatibility limits and backing-texture composition cost.
5. Native Metal adapter — production Metal engines on macOS; hide Objective-C++/CAMetalLayer
   behind a portable C++/Qt interface.

## Workflow

### 1. Assess

- Identify task type; for rendering tasks, pick one integration path from
  [Renderer integration choice](#renderer-integration-choice).

### 2. Implement

- Provide a minimal buildable slice: CMake target, source/header/ui files, test target when
  relevant, and exact configure/build/test commands.
- Follow the incremental loop in
  [workflow-testing-debugging.md](references/workflow-testing-debugging.md#2-implementation-workflow);
  apply the other references as [Reference routing](#reference-routing) directs.

### 3. Verify

- When a terminal is available, run the qt-cmake trio after each slice:

  ```bash
  qt-cmake -S . -B build/debug -G Ninja -DCMAKE_BUILD_TYPE=Debug
  cmake --build build/debug --parallel
  ctest --test-dir build/debug --output-on-failure
  ```

- Complete the quality bar in
  [toolchain-cmake.md](references/toolchain-cmake.md#7-ci-and-quality-gates) and the
  completion checklist in
  [workflow-testing-debugging.md](references/workflow-testing-debugging.md#6-completion-checklist).
  State any unverified areas explicitly.
- For reviews, report findings by category: correctness, ownership/lifecycle, threading, API
  misuse, UI/UX, rendering integration, performance, build/test. Cite files/lines, distinguish
  confirmed defects from style preferences, and give concrete fixes plus the command that
  would catch the issue next time.
- For debugging, start with Qt logs (`QT_LOGGING_RULES`, `qt.vulkan`, `qt.rhi.general`), then
  Vulkan validation or Metal frame capture. Ask for logs only when missing data blocks progress.

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
[api-framework.md](references/api-framework.md) too.

## Resources

External: [Build with CMake](https://doc.qt.io/qt-6/cmake-manual.html).
