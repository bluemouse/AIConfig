# Qt 6 CMake and toolchain reference

## Table of contents

1. Required build policy
2. Minimal widgets application CMake
3. Rendering-oriented target layout
4. Designer, moc, resources, and shaders
5. Configure, build, test
6. Platform notes
7. CI and quality gates

## 1. Required build policy

Use CMake only. Do not generate qmake examples. Do not use `qt5_*` commands. Use Qt 6 target names and commands. Follow the [Build with CMake](https://doc.qt.io/qt-6/cmake-manual.html) manual for imported targets, policies, and command reference.

Default baseline:

- C++17 or newer, because Qt 6 requires C++17-capable compilers.
- `find_package(Qt6 REQUIRED COMPONENTS Core Gui Widgets Test)` as needed.
- `qt_standard_project_setup()` for common Qt defaults, including AUTOMOC/AUTOUIC behavior.
- `qt_add_executable()` or `qt_add_library()` for Qt targets.
- `target_link_libraries(... PRIVATE Qt6::Widgets Qt6::Gui Qt6::Core)` and `Qt6::Test` for test targets.
- `set_target_properties(app PROPERTIES WIN32_EXECUTABLE ON MACOSX_BUNDLE ON)` for desktop GUI apps.

## 2. Minimal widgets application CMake

```cmake
cmake_minimum_required(VERSION 3.21)
project(RenderTool VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

find_package(Qt6 REQUIRED COMPONENTS Core Gui Widgets)

qt_standard_project_setup()

qt_add_executable(render_tool
    src/main.cpp
    src/MainWindow.h
    src/MainWindow.cpp
    src/MainWindow.ui
)

target_link_libraries(render_tool
    PRIVATE
        Qt6::Core
        Qt6::Gui
        Qt6::Widgets
)

set_target_properties(render_tool PROPERTIES
    WIN32_EXECUTABLE ON
    MACOSX_BUNDLE ON
)
```

Add `Test` to `find_package` and a `tst_*` target when tests are needed (see §4).

Use `CMAKE_CXX_STANDARD 20` when the project allows it; otherwise use 17. Do not write compatibility paths for older Qt or older compilers unless the user explicitly gives a team baseline.

## 3. Rendering-oriented target layout

Separate portable UI, platform glue, and rendering engine integration:

```text
src/
  app/                 QApplication, MainWindow, actions, settings
  ui/                  widgets, panels, dialogs, models, delegates
  viewport/            Qt-facing viewport widget/window adapters
  render_bridge/       QObject-safe command/state bridge to renderer
  platform/macos/      Objective-C++ Metal surface/layer adapter
  platform/vulkan/     Vulkan surface/window adapter
  tests/               Qt Test targets
```

Recommended target split:

```cmake
qt_add_library(render_tool_ui STATIC
    src/app/MainWindow.cpp
    src/app/MainWindow.h
    src/app/MainWindow.ui
    src/ui/SceneModel.cpp
    src/ui/SceneModel.h
    src/viewport/RenderViewportWidget.cpp
    src/viewport/RenderViewportWidget.h
)

target_link_libraries(render_tool_ui
    PUBLIC Qt6::Core Qt6::Gui Qt6::Widgets
    PRIVATE render_engine
)
```

Keep engine targets independent from Widgets when possible. UI targets may depend on engine interfaces; renderer internals should not depend on `QWidget`.

## 4. Designer, moc, resources, and shaders

- `moc`: triggered automatically for headers/sources containing `Q_OBJECT` when AUTOMOC is enabled by `qt_standard_project_setup()`.
- `uic`: triggered automatically for `.ui` files when AUTOUIC is enabled. Add `.ui` files to target sources.
- `rcc`: use `qt_add_resources()` for icons, styles, static test data, and small UI assets.
- `qsb`/Shader Tools: only use when implementing Qt QRhi/QRhiWidget rendering. If shaders belong to the external Vulkan/Metal engine, build them in the engine's shader pipeline instead.

Resource example:

```cmake
qt_add_resources(render_tool "ui_assets"
    PREFIX "/"
    FILES
        resources/icons/open.svg
        resources/icons/play.svg
)
```

Test target example:

```cmake
qt_add_executable(tst_scene_model
    tests/tst_scene_model.cpp
)
target_link_libraries(tst_scene_model PRIVATE render_tool_ui Qt6::Test)
add_test(NAME scene_model COMMAND tst_scene_model)
```

## 5. Configure, build, test

Prefer `qt-cmake` from the selected Qt installation when available, because it supplies the Qt prefix automatically.

```bash
qt-cmake -S . -B build/debug -G Ninja -DCMAKE_BUILD_TYPE=Debug
cmake --build build/debug --parallel
ctest --test-dir build/debug --output-on-failure
```

Alternative with plain CMake:

```bash
cmake -S . -B build/debug -G Ninja \
  -DCMAKE_PREFIX_PATH=/path/to/Qt/6.x/platform \
  -DCMAKE_BUILD_TYPE=Debug
cmake --build build/debug --parallel
ctest --test-dir build/debug --output-on-failure
```

Multi-config generators:

```bash
qt-cmake -S . -B build -G "Ninja Multi-Config"
cmake --build build --config Debug --parallel
ctest --test-dir build -C Debug --output-on-failure
```

## 6. Platform notes

Linux:

- Use Ninja or the team's generator baseline.
- Ensure platform plugins and shared libraries are found at runtime in development environments.
- Use Vulkan SDK and validation layers for Vulkan paths.

Windows:

- Set `WIN32_EXECUTABLE ON` for GUI apps.
- Keep MSVC runtime, Qt runtime, plugins, and Vulkan SDK configuration explicit in development documentation.
- Use `windeployqt` for packaging when producing distributable builds.

macOS:

- Set `MACOSX_BUNDLE ON`.
- Keep Metal adapter code in Objective-C++ `.mm` files behind a small C++ interface.
- Use `macdeployqt` or the team's packaging system for bundles.
- Do not mix portable widgets code with Cocoa/Metal headers except in platform adapter files.

## 7. CI and quality gates

Minimum gates for generated or modified Qt code:

```bash
cmake --build build/debug --parallel
ctest --test-dir build/debug --output-on-failure
```

Recommended additional gates:

- `clang-format` or the repository formatter.
- `clang-tidy` on changed C++ files with Qt-aware suppressions.
- compiler warnings as errors for project code, not third-party code.
- sanitizers for non-GUI unit tests where supported.
- Vulkan validation and Metal validation in graphics test runs.
- smoke launch test with `QT_LOGGING_RULES` set for relevant categories.
