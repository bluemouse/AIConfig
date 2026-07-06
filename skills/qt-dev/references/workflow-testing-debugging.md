# Planning, coding, testing, and debugging workflow

## Table of contents

1. Planning workflow
2. Implementation workflow
3. Testing strategy
4. Debugging workflow
5. Review workflow
6. Completion checklist

## 1. Planning workflow

Before writing significant Qt code, identify:

- target platforms: Linux, Windows, macOS.
- top-level UI shape: main window, central viewport, docks, menus, toolbars, dialogs.
- rendering integration path: `QVulkanWindow`, custom Vulkan `QWindow`, `QRhiWidget`, native Metal adapter, or engine-owned surface.
- ownership: which layer owns `QWidget`, `QWindow`, native surface/layer, graphics device, swapchain/drawable, GPU resources.
- thread model: GUI thread, render thread, worker threads, and signal/queue boundaries.
- data model: scene/resource IDs, models/views/delegates, property editing flow.
- test plan: unit tests, model tests, UI smoke tests, renderer integration smoke tests.

For UI work, ask missing high-impact questions only when they block implementation: target desktop platform emphasis, main user workflow, required panels, input devices, localization, accessibility, and design-system constraints.

## 2. Implementation workflow

Use an incremental loop:

1. Add or update CMake targets first.
2. Build a minimal `QApplication` + `QMainWindow` shell.
3. Add actions/menus/toolbar/status/docks.
4. Add models and panels with fake or small data.
5. Add viewport placeholder.
6. Integrate renderer adapter behind an interface.
7. Wire commands and state with queued signals.
8. Add tests for models/controllers before renderer-heavy tests.
9. Enable logging and debug categories before chasing rendering issues.
10. Run build/tests after each slice.

Do not let the first implementation combine UI layout, renderer initialization, shader compilation, asset loading, and persistence in one class.

## 3. Testing strategy

Use Qt Test + CTest.

Unit-test candidates:

- models: row/column counts, data roles, begin/end mutation behavior, stable IDs.
- controllers: command validation, state transitions, error propagation.
- settings: save/restore round trips.
- dialogs/panels: validators and signal emission.
- render bridge: resize command generation, high-DPI calculations, engine command serialization.

Qt Test patterns:

- Test classes inherit `QObject` and expose private slots as tests.
- Use `initTestCase()`/`cleanupTestCase()` for suite-level setup/teardown.
- Use `init()`/`cleanup()` for per-test setup/teardown.
- Use `QSignalSpy` for signal emission and async waits; verify `spy.isValid()` before assertions.
- Use CTest `add_test()` for every test executable.
- Use `-platform offscreen` only for tests that are known to work without real window-system behavior; rendering/windowing tests often need real platform support.

Example test skeleton:

```cpp
class tst_SceneModel final : public QObject
{
    Q_OBJECT
private slots:
    void rowCount_emptyScene_isZero();
    void addNode_emitsRowsInserted();
};
```

## 4. Debugging workflow

Start with reproducible basics:

1. Capture exact Qt version, OS, GPU, graphics API, build type, and command line.
2. Reproduce from a clean build directory.
3. Turn on relevant Qt logging: `QT_LOGGING_RULES="qt.vulkan=true;qt.rhi.general=true"` when applicable.
4. Check CMake target links, plugin availability, platform plugin load, and runtime library paths.
5. For Vulkan, enable validation layers before `QVulkanInstance::create()`.
6. For Metal, use Xcode/Metal validation and frame capture.
7. For GUI issues, inspect object ownership, parent/child trees, thread affinity, and signal connection types.
8. For hangs, look for blocking work in GUI thread, direct cross-thread calls, GPU waits, or nested event loops.
9. For crashes on close/resize, inspect surface destruction and teardown ordering.

Common issue matrix:

| Symptom | Likely area | First checks |
|---|---|---|
| UI freezes during loading | GUI thread blocked | move import/compile to worker; emit progress |
| viewport black after resize | swapchain/drawable | physical size, DPR, resize event, surface validity |
| crash on exit | ownership/lifetime | parent tree, render thread stop, swapchain release before window destroy |
| shortcut missing in viewport | focus/container | action context, focus proxy, event forwarding |
| Vulkan instance/surface fails | platform/Vulkan setup | Vulkan SDK, validation layers, `qt.vulkan`, instance extensions |
| Metal flicker/wrong size | layer sizing | drawable size = logical size * DPR, resize throttling |

## 5. Review workflow

When reviewing code, inspect in this order:

1. Build system: Qt 6, CMake targets, module links, AUTOMOC/AUTOUIC, no qmake/Qt5/QML.
2. Ownership/lifetime: QObject parents, RAII, render thread shutdown, surface/swapchain lifetime.
3. Threading: widgets only on GUI thread, queued connections across threads, no unsynchronized shared containers.
4. API correctness: signals/slots, model/view contracts, event handlers call base where needed.
5. UI/UX: layouts, keyboard navigation, actions/shortcuts, accessibility names, persistent geometry/settings.
6. Rendering integration: chosen path is appropriate, high-DPI handled, validation/capture enabled, no excessive readbacks.
7. Performance: no heavy work in `paintEvent`, `resizeEvent`, `data()`, or hot signal handlers.
8. Tests: CTest targets, model/controller coverage, smoke tests for viewport and shutdown.

## 6. Completion checklist

Before presenting final code or guidance, confirm:

- The answer stays within Qt 6 + CMake + Widgets/no QML.
- CMake contains the correct Qt modules and target links.
- QObject subclasses have `Q_OBJECT`, noncopyability, and clear ownership.
- UI code uses layouts and action-based commands.
- Rendering integration names who owns the native graphics handles.
- Resize/high-DPI/surface-destroy paths are addressed for viewport code.
- Tests or at least test hooks are described.
- Debugging instructions include both Qt logs and native graphics validation when relevant.
