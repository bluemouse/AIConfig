# Qt 6 rendering application architecture for Vulkan and Metal

## Table of contents

1. Qt's role in rendering applications
2. Integration decision tree
3. Vulkan patterns
4. Metal patterns
5. Embedding render surfaces in widget UIs
6. Threading and data flow
7. Resize, high-DPI, and lifetime handling
8. Debugging and profiling
9. Rendering-specific best practices

## 1. Qt's role in rendering applications

Use Qt for application UI/UX: main window, menus, actions, docking panels, property editors,
scene/resource inspectors, logs, settings, file dialogs, platform integration, and input event
capture. Keep Vulkan/Metal rendering ownership in the renderer unless deliberately using
Qt-managed rendering helpers. For device/memory/barriers/pipelines inside the engine, use
[vulkan-dev](../../vulkan-dev/SKILL.md) or native Metal tooling — this document covers Qt-hosted
viewport integration only.

A rendering tool commonly has this structure:

```text
QApplication
  MainWindow
    menus/toolbars/actions
    dock widgets: scene tree, properties, assets, log, frame profiler
    central render viewport: QWidget container around QWindow, QRhiWidget, or native adapter
  RenderController : QObject
    queued UI commands -> renderer
    renderer state/progress -> queued UI signals
  Renderer/Engine
    owns device, swapchain/layer, pipelines, resources, frame graph
```

## 2. Integration decision tree

Choose one path and make the ownership explicit:

1. `QVulkanWindow`: choose for simple Vulkan examples, tools, or prototypes where Qt may own the Vulkan device, queue, command pool, depth/stencil image, and swapchain.
2. Custom `QWindow` + `QVulkanInstance`: choose for production Vulkan engines where the engine owns device/swapchain details but wants Qt to provide cross-platform window/surface creation.
3. `QWidget::createWindowContainer(QWindow*)`: choose when a `QWindow` viewport must live inside a Widgets UI. Use one primary viewport and avoid overlapping widget overlays.
4. `QRhiWidget`: choose for Qt-managed widget-composited preview rendering using Vulkan or Metal, accepting QRhi compatibility limits and extra backing texture/composition cost.
5. Native Metal adapter: choose for production Metal engines on macOS. Hide Objective-C++ and CAMetalLayer/MTKView details behind a portable C++/Qt interface.

Do not use QML/Qt Quick for any of these paths.

## 3. Vulkan patterns

### QVulkanWindow pattern

Use when Qt can manage the core Vulkan windowing objects. Implement a `QVulkanWindowRenderer` and return it from a `QVulkanWindow` subclass.

Required behavior:

- Create `QVulkanInstance` early, typically in `main()`.
- Enable validation layers before `QVulkanInstance::create()` in debug builds.
- Call `window.setVulkanInstance(&instance)` before showing the window.
- Put per-device resources in `initResources()` and release them in `releaseResources()`.
- Put swapchain-size-dependent resources in `initSwapChainResources()` and release them in `releaseSwapChainResources()`.
- Record commands in `startNextFrame()` into `currentCommandBuffer()` and call `frameReady()` exactly once.
- Call `requestUpdate()` after `frameReady()` for continuous rendering; otherwise render on demand.
- Use `currentFrame()`/`concurrentFrameCount()` to double/triple-buffer uniforms and transient resources.

### Custom Vulkan QWindow pattern

Use when the engine owns Vulkan.

Required behavior:

- Subclass `QWindow`.
- In the constructor, call `setSurfaceType(QSurface::VulkanSurface)` before the native surface is created.
- Associate a live `QVulkanInstance` with `QWindow::setVulkanInstance()`; the instance must outlive the window.
- Use `QVulkanInstance::surfaceForWindow(this)` to obtain `VkSurfaceKHR` without writing platform-specific WSI code.
- Use `QVulkanInstance::supportsPresent(physicalDevice, queueFamilyIndex, window)` when
  selecting queue families; pass the target `QWindow` so present support is checked for the
  actual surface.
- Handle `exposeEvent`, resize, device-pixel-ratio changes, and `QPlatformSurfaceEvent::SurfaceAboutToBeDestroyed`.
- Do not assume a surface, swapchain, or native window remains valid after hide, destroy, screen move, DPI change, or platform-surface events.

## 4. Metal patterns

Qt Widgets has no direct public `QMetalWindow` equivalent to `QVulkanWindow`. Use one of these patterns:

- For Qt-managed preview rendering, use `QRhiWidget` and select `QRhiWidget::Api::Metal` on macOS when QRhi is acceptable.
- For a production Metal engine, create a native macOS rendering adapter in Objective-C++ (`.mm`) that owns the Metal device/queue/layer/view and expose only a narrow C++/Qt-facing interface.
- Keep native Cocoa/Metal includes out of portable UI headers. Use pimpl or an abstract `IRenderSurface` interface.
- Treat Qt native interfaces as version-coupled. If used, isolate them in the platform adapter and test on the exact Qt version shipped.
- Keep all CAMetalLayer drawable-size updates tied to Qt window/widget resize and device-pixel-ratio changes.

A portable Qt-facing class should look like a QObject/controller, not like a Metal object:

```cpp
class MetalViewportController final : public QObject
{
    Q_OBJECT
    Q_DISABLE_COPY_MOVE(MetalViewportController)
public:
    explicit MetalViewportController(QObject *parent = nullptr);
    void attachTo(QWidget *hostWidget); // implemented by platform adapter
    void resizeDrawable(QSize logicalSize, qreal devicePixelRatio);

signals:
    void frameStatsUpdated(FrameStats stats);
    void renderError(QString message);
};
```

## 5. Embedding render surfaces in widget UIs

`QWidget::createWindowContainer()` is useful but not transparent. Design around its limitations:

- The embedded window is a native child window and behaves as an opaque box above the widget hierarchy.
- Stacking order with overlapping widgets or multiple containers is limited/undefined.
- Focus transfer is platform-dependent; explicitly route shortcuts and focus transitions.
- Many native child windows can hurt performance; use one main viewport where possible.
- Do not put the viewport container inside complex scrolling/MDI layouts unless there is a tested reason.
- Do not draw semi-transparent widgets over the native viewport. Use dock panels, sidebars, or renderer-drawn overlays.

Good layout:

```text
QMainWindow
  central: QWidget with QVBoxLayout
    toolbar/viewport status strip as normal widgets
    one viewport container filling remaining area
  docks: scene tree, properties, resources, logs
```

## 6. Threading and data flow

Recommended split:

- GUI thread owns all `QWidget`, `QWindow`, `QAction`, models, dialogs, and settings.
- Render thread owns command recording, GPU synchronization, resource upload, and frame execution if the engine architecture requires it.
- Asset/import worker threads do CPU-heavy parsing and emit immutable results.

Use queued Qt signals or explicit thread-safe queues for communication. Do not let worker threads call widget methods. Do not expose raw engine pointers to models or delegates without lifetime guarantees.

Command pattern:

```cpp
struct ViewportCommand {
    enum class Type { LoadScene, SetCamera, SetSelection, Resize, ToggleOverlay } type;
    QVariant payload;
};
```

Use stable IDs for scene objects/resources in UI models; resolve IDs inside the engine under the engine's synchronization rules.

## 7. Resize, high-DPI, and lifetime handling

For every viewport integration, handle:

- logical size from Qt widgets/windows.
- physical framebuffer/drawable size = logical size * device-pixel ratio.
- `QEvent::DevicePixelRatioChange` and screen moves.
- minimized/unexposed windows: pause expensive rendering and avoid swapchain churn.
- platform surface destruction: release swapchain/layer-bound objects before the native surface disappears.
- renderer shutdown before Qt tears down the window/container.

Always document ownership:

```cpp
// Qt owns m_window through createWindowContainer().
// Engine owns VkDevice/VkSwapchainKHR. VkSurfaceKHR is obtained from Qt and is valid only while the QWindow native surface is valid.
```

## 8. Debugging and profiling

Vulkan:

- Enable `VK_LAYER_KHRONOS_validation` before creating `QVulkanInstance` in debug builds.
- Enable Qt logging category `qt.vulkan` while diagnosing instance/surface/window integration.
- Use RenderDoc or vendor GPU tools for frame captures on Linux/Windows.
- Name Vulkan objects and command sections in the engine for readable captures.

Metal:

- Run under Xcode with Metal validation/debugging enabled or use `METAL_DEVICE_WRAPPER_TYPE=1` when applicable.
- Use Xcode GPU Frame Capture for frame inspection.
- Use `MTL_HUD_ENABLED=1` on supported macOS versions for quick overlay diagnostics.

Qt/RHI:

- Enable `QT_LOGGING_RULES="qt.rhi.general=true"` when using QRhi/QRhiWidget.
- Use QRhi leak checks and resource names for QRhi-owned rendering.
- Treat QRhi error returns and soft failures as control flow, not asserts.

## 9. Rendering-specific best practices

- Keep the renderer independent of QWidget classes. Depend on narrow viewport/surface abstractions.
- Avoid Qt containers in hot render loops unless profiling says they are acceptable.
- Use `QElapsedTimer` for CPU timing in UI/controller code; use GPU timestamps/vendor tools for GPU timing.
- Avoid synchronous readbacks in interactive paths. Screenshot/readback APIs are for tools/tests, not per-frame UI.
- Never rebuild pipelines, descriptor layouts, or heavy GPU resources from every paint/update event.
- Debounce UI controls that trigger expensive renderer rebuilds.
- Keep render settings changes transactional: validate in UI, send a command, apply on render boundary, then emit success/failure.
- Capture enough renderer state in logs to reproduce failures: Qt version, platform, GPU, backend, devicePixelRatio, swapchain size, validation status.
