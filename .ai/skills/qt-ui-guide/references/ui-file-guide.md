# Qt Widgets Designer `.ui` File Guide

Use this whenever creating or editing Designer XML.

## Scope

A `.ui` file should express stable presentation structure. Do not encode application business logic into XML.

Qt Widgets Designer `.ui` files are XML representations of the widget tree and can be processed by `uic` at build time or loaded dynamically.

Official reference:
- https://doc.qt.io/qt-6/designer-using-a-ui-file.html

## Required shape

Use the standard Designer form:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>ExampleDialog</class>
 <widget class="QDialog" name="ExampleDialog">
  ...
 </widget>
 <resources/>
 <connections/>
</ui>
```

Use a descriptive form class and object names. Keep XML formatted in the conventional Designer style.

## Layout rules

- Give `QWidget`/`QDialog` forms a top-level layout.
- For `QMainWindow`, create `centralwidget` and give it a layout.
- Do not assign manual geometry to ordinary child widgets that should resize with their layout.
- Geometry on the top-level widget is acceptable as Designer's initial preview size; do not treat it as a hard runtime size.
- Use layout margins, spacing, stretch, spacers, and size policies instead of fixed child coordinates.
- Use `QSplitter` when user-controlled pane resizing is part of the design.

## Object naming

Use lower camel case for child objects and a descriptive form name for the top level.

Good:

- `searchEdit`
- `resultsView`
- `propertiesGroup`
- `applyButton`
- `buttonBox`

Avoid:

- `pushButton_7`
- `widget_3`
- names that describe color/position instead of purpose

Use stable object names because C++, UI tests, accessibility tooling, and styles may refer to them.

## Text and translation

Use normal `<string>` properties for user-facing text so `retranslateUi()` can handle translations.

Use `notr="true"` only for genuinely non-translatable data.

Use ampersand mnemonics intentionally in labels/actions when appropriate, for example `&Name:`. Escape XML ampersands as `&amp;`.

For labeled fields, set the `QLabel` `buddy` property to the target object's name.

## Dialog buttons

Prefer `QDialogButtonBox` standard buttons. Example:

```xml
<widget class="QDialogButtonBox" name="buttonBox">
 <property name="orientation">
  <enum>Qt::Horizontal</enum>
 </property>
 <property name="standardButtons">
  <set>QDialogButtonBox::Cancel|QDialogButtonBox::Ok</set>
 </property>
</widget>
```

Do not manually arrange OK/Cancel buttons to a fixed platform order.

## Tab order

When focus order is not naturally correct, include a `<tabstops>` section:

```xml
<tabstops>
 <tabstop>nameEdit</tabstop>
 <tabstop>typeCombo</tabstop>
 <tabstop>enabledCheck</tabstop>
</tabstops>
```

Do not include labels or non-focusable controls.

## Actions

For `QMainWindow`, declare reusable commands as `QAction` objects and reference them from menus/toolbars when appropriate. Keep command handlers in C++.

Use standard shortcuts in C++ with `QKeySequence::StandardKey` if the `.ui` representation would force a platform-specific literal shortcut.

## Resources and icons

Prefer `QIcon` resources through the project's `.qrc` or existing icon system. Do not embed fragile absolute file system paths.

For a new form when resource paths are not yet known, omit decorative icons rather than inventing asset paths.

## Connections

Keep `<connections>` empty unless the connection is static, local, and presentation-level. Common acceptable examples include a dialog button box's accepted/rejected signals wired to the dialog's accept/reject slots.

Prefer C++ for application actions, validation, model updates, and conditional behavior.

## Custom widgets

If an existing repository uses promoted widgets, preserve its `<customwidgets>` declarations.

Do not invent a custom widget class unless the user requested it or the repository already provides it.

## Validation

Always run:

```bash
python <SKILL_ROOT>/scripts/validate_ui.py path/to/form.ui
```

If the project's `uic` executable is available, also run:

```bash
uic path/to/form.ui -o /tmp/ui_form.h
```

A passing Python check means the file is structurally well-formed and satisfies common layout/naming checks. Only a successful `uic` invocation or Designer load validates compatibility with the installed Qt toolchain.
