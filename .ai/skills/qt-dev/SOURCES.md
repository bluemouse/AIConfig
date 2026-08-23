# Sources

## Qt Core module overview

- **URL:** https://doc.qt.io/qt-6/qtcore-index.html
- **Last reviewed:** 2026-07-06
- **Used for:**
  - `SKILL.md` → operating model, non-negotiable constraints
  - `references/api-framework.md` → Core module map, object model, threading, containers
- **Aspects extracted:**
  - Signals/slots, properties, object trees, threading, resources → `references/api-framework.md`
  - `find_package(Qt6 REQUIRED COMPONENTS Core)` and `Qt6::Core` linking → `references/toolchain-cmake.md`

## Qt GUI module overview

- **URL:** https://doc.qt.io/qt-6/qtgui-index.html
- **Last reviewed:** 2026-07-06
- **Used for:**
  - `references/api-framework.md` → Gui module map, QWindow, input, Vulkan integration
  - `references/rendering-vulkan-metal.md` → QVulkanInstance, QVulkanWindow, RHI/Vulkan paths
- **Aspects extracted:**
  - Windowing, events, low-level graphics, OpenGL/RHI/Vulkan integration → `references/api-framework.md`
  - `find_package(Qt6 REQUIRED COMPONENTS Gui)` and `Qt6::Gui` linking → `references/toolchain-cmake.md`

## Qt Widgets module overview

- **URL:** https://doc.qt.io/qt-6/qtwidgets-index.html
- **Last reviewed:** 2026-07-06
- **Used for:**
  - `SKILL.md` → scope (Widgets-only, no QML), When to Use
  - `references/api-framework.md` → widgets framework, layouts, model/view, Designer
  - `references/best-practices.md` → UI/UX design for desktop tools
- **Aspects extracted:**
  - Classic desktop UI elements, layouts, styles, model/view, Graphics View → `references/api-framework.md`
  - `find_package(Qt6 REQUIRED COMPONENTS Widgets)` and `Qt6::Widgets` linking → `references/toolchain-cmake.md`

## Build with CMake (Qt 6)

- **URL:** https://doc.qt.io/qt-6/cmake-manual.html
- **Last reviewed:** 2026-07-06
- **Used for:**
  - `SKILL.md` → tool usage, CMake-only policy
  - `references/toolchain-cmake.md` → build policy, configure/build/test commands
  - `scripts/qt_cmake_plan.py` → skeleton CMake output
- **Aspects extracted:**
  - `qt_standard_project_setup()`, `qt_add_executable()`, imported targets → `references/toolchain-cmake.md`
  - `qt-cmake` and command-line configure/build workflow → `references/toolchain-cmake.md`, `scripts/qt_cmake_plan.py`

## Additional Qt documentation (synthesis metadata)

- **Sources:** Qt Widgets Designer manual, Qt Test docs, QVulkanWindow, QVulkanInstance, QWindow,
  QWidget, QRhi, QRhiWidget, QNativeInterface, QSignalSpy pages
- **Last reviewed:** 2026-07-06
- **Used for:**
  - `references/api-framework.md` → Designer, model/view, render-surface APIs
  - `references/rendering-vulkan-metal.md` → integration patterns and lifetime handling
  - `references/workflow-testing-debugging.md` → Qt Test + CTest workflow
- **Access limitation:** Individual API pages were cross-checked against template content; module
  overviews above are the primary verified anchors.

## TheQtCompanyRnD qt-cpp-review (synthesis metadata)

- **URL:** https://github.com/TheQtCompanyRnD/qt-cpp-review
- **Last reviewed:** 2026-07-06
- **Used for:**
  - Review categories in `references/workflow-testing-debugging.md` and `references/best-practices.md`
- **Aspects extracted:**
  - Ownership, threading, API correctness, error handling, performance, confidence-based reporting

## TheQtCompanyRnD qt-project (synthesis metadata)

- **URL:** https://github.com/TheQtCompanyRnD/qt-project
- **Last reviewed:** 2026-07-06
- **Used for:**
  - `references/toolchain-cmake.md` → modern Qt 6 CMake layout
- **Access limitation:** Raw `SKILL.md` fetch returned a cache error. Patterns adapted from README/folder
  structure: prefer Qt 6 CMake commands, reject qmake and Qt 5 macros.

## TheQtCompanyRnD qt-ui-design (synthesis metadata)

- **URL:** https://github.com/TheQtCompanyRnD/qt-ui-design
- **Last reviewed:** 2026-07-06
- **Used for:**
  - `references/best-practices.md` → Widgets UI/UX intake and audit ideas
- **Aspects extracted:**
  - Desktop Widgets UI/UX guidance only; QML/Qt Quick content intentionally excluded

## Mte90 qt-cpp (not used)

- **URL:** https://github.com/Mte90/qt-cpp
- **Last reviewed:** 2026-07-06
- **Access limitation:** GitHub page/raw files failed through the available fetcher; not used as a
  verified source.

## Scope decisions

- QML/Qt Quick content was omitted even when present in source material.
- Qt 5 and porting guidance were omitted.
- QRhi/QRhiWidget content is included because Qt 6 exposes QRhiWidget as a public Widgets API and
  it is relevant to Vulkan/Metal preview rendering. The skill warns about QRhi compatibility and
  integration constraints.
- Metal guidance is framed as Qt-hosted native integration because Qt Widgets does not provide a
  direct public `QMetalWindow` counterpart to `QVulkanWindow`.
