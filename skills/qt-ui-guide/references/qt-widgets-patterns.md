# Qt Widgets Design and Implementation Patterns

This guide targets Qt 6 C++ and Qt Widgets. Prefer the repository's established Qt version when it differs.

## Layouts and sizing

Use layouts for all resizable content. Qt layouts distribute space using size hints, minimum sizes, size policies, stretch factors, and spacers.

Prefer:

- `QVBoxLayout` / `QHBoxLayout` for linear structure
- `QFormLayout` for label-field pairs
- `QGridLayout` for true row/column relationships
- `QStackedWidget` for alternate pages controlled by navigation or mode
- `QSplitter` when users need to resize adjacent panes

Avoid fixed width/height unless the content has a real invariant. A top-level form should have a top-level layout. In a `QMainWindow`, place application content inside `centralWidget` and give the central widget a layout.

Use layout margins and spacing consistently. Prefer style-provided defaults unless the application has a design system.

Official references:
- https://doc.qt.io/qt-6/layout.html
- https://doc.qt.io/qt-6/designer-layouts.html
- https://doc.qt.io/qt-6/qsizepolicy.html

## Choosing containers

Use `QMainWindow` for full desktop application windows that need menus, toolbars, status bars, and dock widgets.

Use `QDialog` for bounded tasks that are completed, accepted, cancelled, or closed.

Use `QDockWidget` for auxiliary tool panels users may move, resize, hide, or dock.

Use `QSplitter` for primary adjacent work areas where resizing is part of the workflow.

Use `QTabWidget` for a small number of peer views when users benefit from visible labels. Avoid deep nested tabs.

Use `QGroupBox` when the group itself has a meaningful label or enabled/disabled state. Do not box every cluster; spacing often communicates grouping better.

Use `QScrollArea` when content may exceed available space and cannot be better restructured. Avoid making the whole application window a giant scrolling form when navigation or sections would be clearer.

## Dialog actions

Use `QDialogButtonBox` with standard buttons and roles. It adapts ordering to the current platform style.

Typical pattern:

- `Ok` / `Save` / `Open`: accept role
- `Cancel` / `Close`: reject role
- `Apply`: apply without closing
- `Reset`: reset current values
- destructive custom action: destructive role when appropriate

Connect accept/reject semantics to `QDialog::accept()` and `QDialog::reject()` in C++ or simple Designer connections.

Do not manually force Windows-style or macOS-style button order.

Official reference:
- https://doc.qt.io/qt-6/qdialogbuttonbox.html

## Commands, menus, toolbars, and shortcuts

Represent reusable commands with `QAction`. Share the same action among menus, toolbars, and context menus so enabled/checked state, text, icon, and shortcut remain synchronized.

Prefer `QKeySequence::StandardKey` for standard operations such as Open, Save, Close, Copy, Paste, Undo, Redo, Find, and Help. Qt maps standard keys to platform conventions.

For non-standard shortcuts:

- make them discoverable in menus/tooltips
- avoid conflicts
- do not hard-code a platform-specific modifier assumption when Qt can express it portably

Official reference:
- https://doc.qt.io/qt-6/qkeysequence.html

## Forms and data entry

Use `QLabel` plus buddy relationships for text fields and other focusable controls.

Choose controls by semantics:

- `QLineEdit`: short text
- `QPlainTextEdit`: larger plain text
- `QTextEdit`: rich text
- `QSpinBox` / `QDoubleSpinBox`: bounded precise numeric values
- `QSlider`: continuous/approximate adjustment, often paired with a precise numeric control
- `QComboBox`: one value from a list
- `QCheckBox`: independent boolean state
- radio buttons in a `QButtonGroup`: small exclusive set
- `QDateEdit`, `QTimeEdit`, `QDateTimeEdit`: dates/times
- `QFontComboBox`, color picker patterns, or domain-specific editors when the value type warrants them

Show units next to numeric values or use suffix properties where appropriate. Do not put units only in placeholder text.

Validate near the field. Explain constraints before submission when they are predictable.

## Lists, trees, and tables

For non-trivial data, prefer model/view:

- `QListView`
- `QTreeView`
- `QTableView`
- a `QAbstractItemModel`, `QAbstractListModel`, or `QAbstractTableModel` subclass
- proxy models for filtering/sorting
- delegates for specialized presentation/editing

Use convenience item widgets (`QListWidget`, `QTreeWidget`, `QTableWidget`) only for small, local, simple data where synchronization and reuse are not concerns.

Define selection behavior intentionally:

- single vs extended selection
- row vs item selection
- current item vs selected items
- double-click behavior
- Enter activation
- Delete behavior
- context menu commands
- drag/drop semantics

Official references:
- https://doc.qt.io/qt-6/modelview.html
- https://doc.qt.io/qt-6/qabstractitemmodel.html

## Navigation and complex desktop tools

For document-centric or technical tools, separate primary work area from supporting tools.

Useful patterns:

- center: viewport/editor/document
- left: navigation, hierarchy, browser, project tree
- right: properties/inspector
- bottom: output, log, diagnostics, timeline

Use `QDockWidget` when tool placement should be customizable. Use `QSplitter` when pane proportions are essential to the task. Persist user customizations with `QMainWindow::saveState()` / `restoreState()` and `QSettings` when appropriate.

Avoid hard-coding one layout for users who spend long sessions in the application if the workflow naturally benefits from customization.

## State and feedback

Use clear enabled/disabled state and avoid disabling controls without explaining the reason when the user is likely to need them.

For background work:

- display progress if measurable
- otherwise show a busy indicator or explicit busy text
- keep the UI responsive
- expose Cancel if cancellation is technically safe
- report errors near the affected workflow

For document-like content, visibly represent dirty/unsaved state and make Save behavior predictable.

Use status bars for low-priority transient information, not for errors that require action.

## Styling

Start with the current Qt style and platform conventions. Introduce custom styling only to satisfy a product design system or a clear usability need.

When using Qt Style Sheets:

- scope selectors narrowly
- test all widget states: default, hover, pressed, disabled, checked, selected, focus
- test dialogs, menus, scroll bars, item views, tooltips, and high DPI
- avoid fixed dimensions that break font scaling
- remember that Qt Style Sheets are not browser CSS

Prefer semantic palette/style use over hard-coded colors when possible. Use `QStyle` standard metrics and icons when they express the intended platform convention.

Official references:
- https://doc.qt.io/qt-6/stylesheet-reference.html
- https://doc.qt.io/qt-6/qstyle.html

## `.ui` and C++ separation

Use `.ui` for stable structure and declarative properties:

- widget hierarchy
- layouts
- labels/text
- buddy relationships
- simple action/menu structure
- tab order
- standard button configuration

Use C++ for behavior and changing application state:

- model binding
- validation logic
- command handlers
- async operations
- complex enable/visibility rules
- persistence
- dynamic content
- business logic

Do not edit generated `ui_*.h` files. With CMake, use AUTOUIC when that matches the project.

Official reference:
- https://doc.qt.io/qt-6/designer-using-a-ui-file.html

## Custom widgets

Create a custom widget only when standard composition cannot express the interaction well.

A custom widget must define:

- focus policy and keyboard behavior
- size hints and size policy
- mouse/keyboard interaction
- disabled/focus/hover/selected states
- accessible role, name, value, actions, and events as needed
- high-DPI painting and icon behavior
- palette/style integration

If the custom widget must appear in Designer, prefer widget promotion when sufficient; build a Designer plugin only when necessary.

## Performance-aware UI

Do not block the GUI thread with expensive work. For large models or rendering-heavy tools:

- keep UI state changes cheap
- batch model updates appropriately
- avoid rebuilding entire widget trees unnecessarily
- use model/view rather than thousands of child widgets for tabular data
- keep rendering and UI feedback decoupled enough that the user can see progress and cancel work
