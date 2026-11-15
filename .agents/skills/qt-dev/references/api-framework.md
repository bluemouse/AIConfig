# Qt 6 C++ API and framework reference

## Table of contents

1. Required scope
2. Core object model
3. Event loop and threading model
4. Widgets application framework
5. Designer and `.ui` files
6. Model/view for graphics tools
7. QWindow and render-surface APIs
8. API selection checklist

## 1. Required scope

Qt 6 C++ Widgets only — no QML/Qt Quick, no Qt 5 compatibility. For every API answer, name
the module and CMake target. Full scope policy lives in the skill `SKILL.md`.

Minimum module map (aligned with official Qt 6 module overviews):

- `Qt6::Core`: `QObject`, signals/slots, properties, object trees, event loop, timers, files, settings, containers, text, JSON, logging, threads.
- `Qt6::Gui`: windowing integration, input events, screens, icons, images, colors, fonts, actions, low-level graphics, `QVulkanInstance`, `QVulkanWindow`, matrices, native/platform integration.
- `Qt6::Widgets`: classic desktop UI — `QApplication`, `QWidget`, `QMainWindow`, layouts, docks, dialogs, item views, styles, model/view, `QWidget::createWindowContainer()`, `QRhiWidget`.
- `Qt6::Test`: Qt Test and `QSignalSpy`.

Link each module with `find_package(Qt6 REQUIRED COMPONENTS ...)` and `target_link_libraries(... Qt6::Core|Gui|Widgets|Test)` per the [Build with CMake](https://doc.qt.io/qt-6/cmake-manual.html) overview.

## 2. Core object model

Use `QObject` for objects that need signals/slots, dynamic properties, timers, events, or parent-child ownership. Key rules:

- Add `Q_OBJECT` to QObject subclasses with signals, slots, properties, or invokable methods.
- Prefer parent ownership for QObject trees: parent widgets own child widgets; windows/dialogs own their UI objects.
- Use RAII (`std::unique_ptr`, stack objects, custom deleters) for non-QObject resources and native graphics handles.
- Use `QPointer<T>` when observing a QObject that may be deleted elsewhere.
- Disable copying/moving of QObject subclasses with `Q_DISABLE_COPY_MOVE(ClassName)`.
- Use function-pointer connects, not string macros, unless dynamically resolving signals by name.

Canonical connection pattern:

```cpp
connect(action, &QAction::triggered, this, &MainWindow::openScene);
connect(model, &SceneModel::selectionChanged,
        this, &PropertiesPanel::setSelection,
        Qt::QueuedConnection); // required when crossing threads
```

## 3. Event loop and threading model

Qt widgets and windows belong to the GUI thread. Never create, mutate, paint, show, or delete widgets from worker threads. Keep rendering engine work behind a thread-safe boundary:

- GUI thread: widgets, actions, menus, docking, event routing, `QWindow`/container ownership, user-facing state.
- Render thread or engine thread: GPU command preparation, resource uploads, asynchronous shader/asset work.
- Boundary: queued signals/slots, immutable command messages, lock-free queues, mutex-protected state, or atomics.

Do not block the GUI event loop with file I/O, shader compilation, scene import, GPU waits, or synchronous network/IPC. Use progress signals and cancellation.

## 4. Widgets application framework

Prefer a standard desktop graphics-tool shell:

- `QApplication` owns the widget application.
- `QMainWindow` owns `QMenuBar`, `QToolBar`, `QStatusBar`, `QDockWidget`s, and a central viewport/container.
- `QAction` represents commands and is shared across menus, toolbars, shortcuts, and context menus.
- `QDialog` handles modal settings/import/export flows; prefer modeless panels for frequent editing.
- `QSplitter`, `QTabWidget`, and dock widgets are appropriate for renderer tools with viewports, logs, asset browsers, scene trees, and inspectors.
- Use layouts (`QVBoxLayout`, `QHBoxLayout`, `QGridLayout`, `QFormLayout`) instead of absolute geometry.
- Use `QSettings` for persistent UI state such as window geometry, recent files, docks, splitter positions, and renderer preferences.

Typical ownership shape:

```cpp
class MainWindow final : public QMainWindow
{
    Q_OBJECT
    Q_DISABLE_COPY_MOVE(MainWindow)
public:
    explicit MainWindow(QWidget *parent = nullptr);
    ~MainWindow() override;

private:
    void createActions();
    void createDocks();
    QWidget *m_viewportContainer = nullptr; // owned by QObject parent tree
    QPointer<RenderController> m_renderController;
};
```

## 5. Designer and `.ui` files

Use Qt Widgets Designer for stable form layout, not for application architecture.

Rules:

- Add `.ui` files directly to `qt_add_executable()` sources when using CMake AUTOUIC.
- Keep generated `ui_*.h` out of source control unless the project explicitly requires checked-in generated files.
- Do not edit `ui_*.h` manually.
- Put behavior in a C++ wrapper class, not in generated code.
- Use Designer layouts, size policies, tab order, buddies, object names, and widget promotion for custom widgets.
- Promote custom viewport placeholder widgets only when the final widget is a `QWidget`. For a `QWindow`-based renderer, create a container in C++ with `QWidget::createWindowContainer()`.

## 6. Model/view for graphics tools

Use model/view for scene graphs, asset browsers, render passes, resource tables, diagnostics, and property lists.

- Prefer `QAbstractItemModel` for hierarchical scene/resource data.
- Use `QTreeView`, `QTableView`, `QListView`, and delegates instead of manually rebuilding widget trees.
- Emit precise change signals (`dataChanged` with roles, begin/end insert/remove/move) instead of resetting models.
- Keep model data independent from GPU object lifetime. Store stable IDs/handles, not raw pointers to short-lived resources.
- Avoid expensive queries in `data()`; cache derived display values and invalidate deliberately.

## 7. QWindow and render-surface APIs

Use `QWindow` for native rendering surfaces and `QWidget` for surrounding UI. A `QWindow` can be embedded in a widget hierarchy with `QWidget::createWindowContainer()`, but this creates native child-window behavior with limitations.

Important APIs:

- `QWindow::setSurfaceType(QSurface::VulkanSurface)` for a custom Vulkan window.
- `QWindow::setVulkanInstance(QVulkanInstance *)`; the instance must outlive the window.
- `QVulkanInstance::surfaceForWindow(QWindow *)` to obtain `VkSurfaceKHR` without platform-specific WSI code.
- `QWindow::exposeEvent()` and `QWindow::isExposed()` to start/stop expensive rendering.
- `QWindow::devicePixelRatio()` and `QEvent::DevicePixelRatioChange` for high-DPI render target resizing.
- `QPlatformSurfaceEvent::SurfaceAboutToBeDestroyed` for releasing swapchain/surface-bound resources.

## 8. API selection checklist

- Need normal desktop controls: Widgets.
- Need a form: Designer `.ui` + wrapper class.
- Need command reused in menu/toolbar/context/shortcut: `QAction`.
- Need scene/resource tree/table: model/view.
- Need a native render viewport: `QWindow` embedded with `createWindowContainer()` or direct central child window.
- Need simple Qt-managed Vulkan rendering: `QVulkanWindow`.
- Need widget-composited, portable preview rendering: `QRhiWidget`, while accepting QRhi and extra backing texture constraints.
- Need production Metal engine integration: isolate Objective-C++ native Metal surface/layer code behind a platform adapter; keep Qt widgets portable.
