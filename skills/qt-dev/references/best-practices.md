# Qt 6 C++ best practices for desktop rendering tools

## Table of contents

1. Project and architecture
2. QObject ownership and C++ lifetime
3. Signals, slots, and state flow
4. Threading and responsiveness
5. Widgets UI/UX design
6. Model/view and data binding
7. Error handling and logging
8. Performance
9. Rendering integration
10. Anti-patterns to reject
11. Style and review checklist

## 1. Project and architecture

- Separate UI shell, domain model, render bridge, renderer, and platform adapters.
- Keep renderer headers free of `QWidget` dependencies when possible.
- Keep platform-specific Metal/Cocoa code in `.mm` files under a platform directory.
- Use interfaces or pimpl for native graphics surfaces and devices.
- Persist UI state with `QSettings`; do not mix persistent settings into rendering hot paths.
- Use `QAction` as the single source of truth for commands shared by menu, toolbar, context menu, and shortcuts.

## 2. QObject ownership and C++ lifetime

- Parent-owned QObjects are deleted by their parent; do not also delete them with smart pointers.
- Use `std::unique_ptr` for non-QObject resources and renderer-owned objects.
- Use `deleteLater()` when deleting a QObject from event-driven or cross-thread contexts.
- Stop render/worker threads before destroying UI objects they may signal.
- Guard observed QObjects with `QPointer` if lifetime is not strictly parent-owned.
- Avoid raw owning pointers. If a raw pointer appears, document whether it is parent-owned, borrowed, or engine-owned.

## 3. Signals, slots, and state flow

- Use typed connects: `connect(sender, &Sender::signal, receiver, &Receiver::slot)`.
- Use `Qt::QueuedConnection` or default auto connections for cross-thread signals; avoid forced `Qt::DirectConnection` across threads.
- Avoid signal cycles. Add re-entrancy guards when a setter emits a signal that can call back into the setter.
- Emit precise signals after state changes, not before.
- Store `QMetaObject::Connection` only when disconnecting is required.
- Prefer immutable command objects for renderer state changes.

## 4. Threading and responsiveness

- Widgets, windows, and models used by views live on the GUI thread.
- Use workers for import/export, shader compilation, thumbnail generation, and CPU-heavy scene processing.
- Cancel long-running operations cooperatively.
- Never wait on GPU fences or worker futures from the GUI thread unless the UI explicitly enters a modal progress/cancel flow.
- Avoid nested event loops except for standard dialogs.

## 5. Widgets UI/UX design

- Use layouts and size policies; do not hardcode pixel geometry.
- Respect platform conventions for menu placement, shortcuts, dialogs, and window modality.
- Provide keyboard shortcuts for frequent render-tool actions.
- Add accessible names/descriptions for custom controls and viewport-adjacent controls.
- Use dock widgets for inspectors, logs, scene tree, asset browser, and render settings.
- Keep destructive actions confirmable and undoable where practical.
- Avoid styling every widget with style sheets; prefer native style, palette, and targeted custom widgets.
- Do not place translucent floating widgets over a native render window container; use renderer overlays or adjacent Qt panels.

## 6. Model/view and data binding

- Use stable IDs rather than raw renderer pointers in models.
- Emit correct begin/end insert/remove/move signals for structural changes.
- Emit `dataChanged` with specific roles when possible.
- Keep `data()` cheap; avoid renderer queries or filesystem access.
- Cache role-name maps and expensive display strings when used frequently.
- Use delegates for editing and custom display rather than creating many child widgets.

## 7. Error handling and logging

- Check return values for file, JSON, network, renderer initialization, Vulkan instance/surface creation, QRhi creation, and resource creation.
- Use `QLoggingCategory` for project categories such as `app.ui`, `app.render`, `app.vulkan`, `app.metal`, `app.assets`.
- Keep user-facing errors actionable; keep developer logs detailed.
- Include graphics backend, device name, swapchain/drawable size, DPR, and validation status in render initialization logs.
- Do not use `Q_ASSERT` as the only runtime validation for user input, file formats, or device capabilities.

## 8. Performance

- Do not allocate or compile inside high-frequency paint/render/update paths.
- Avoid `QRegularExpression` construction in loops.
- Avoid non-const iteration over implicitly shared containers when reading.
- Avoid repeated `QString` conversions in hot paths.
- Batch UI updates when importing scenes or applying renderer state changes.
- Throttle expensive property changes from sliders/spin boxes before sending them to the renderer.
- Prefer one viewport container; many native child windows harm performance and focus behavior.
- Use frame captures and GPU profilers before optimizing renderer code by guesswork.

## 9. Rendering integration

Follow [rendering-vulkan-metal.md](rendering-vulkan-metal.md) for viewport architecture,
threading, high-DPI, lifetime, and debugging. At minimum:

- Document native handle ownership and validity windows at every Qt boundary.
- Use one thread-safe command boundary from UI to renderer.
- Pause continuous rendering when the window is not exposed/minimized.

## 10. Anti-patterns to reject

Reject or replace these patterns (see skill `SKILL.md` for full scope policy):
- QObject subclass copied or moved.
- Widgets created or mutated from worker/render threads.
- Generated `ui_*.h` manually edited.
- Blocking file import, shader compilation, or GPU waits in slots connected to UI controls.
- Model reset used for every small change.
- Raw renderer pointers stored in item models without lifetime guarantees.
- Multiple overlapping `createWindowContainer()` viewports in one window.
- Metal platform code included from portable Qt widget headers.
- `Q_ASSERT` with side effects or as production error handling.

## 11. Style and review checklist

Before marking Qt work done, confirm:

- Scope: Qt 6 + CMake + Widgets; no qmake, QML, or Qt 5 patterns introduced.
- Ownership: QObject parent trees, RAII for native handles, render thread stopped before UI teardown.
- Threading: widgets/models on GUI thread; cross-thread signals use `Qt::QueuedConnection`.
- UI: layouts and `QAction`-based commands; high-DPI viewport sizing handled.
- Build: correct `find_package` components and `Qt6::*` target links; AUTOMOC/AUTOUIC for `.ui`/headers.
- Tests: Qt Test + CTest for models/controllers when behavior changed.
- Viewport: integration path chosen deliberately; surface/swapchain released before window destroy.
