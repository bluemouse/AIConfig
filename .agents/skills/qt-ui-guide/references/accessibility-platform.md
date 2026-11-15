# Accessibility, Keyboard, High DPI, Localization, and Platform Behavior

## Keyboard access

Every core workflow must be usable without a mouse.

Check:

- logical Tab / Shift+Tab focus order
- visible focus indication
- Enter/Return semantics for default actions
- Escape semantics for cancelling/closing dialogs where appropriate
- arrow-key behavior in lists, trees, tables, tabs, and grouped choices
- Space toggling buttons/checkboxes where standard behavior applies
- discoverable shortcuts for frequent commands

Use `QAction` and `QKeySequence::StandardKey` for standard commands when possible. Do not override common editing/navigation shortcuts without a strong product reason.

## Labels and accessible names

For ordinary labeled fields, use a `QLabel` with a buddy so the mnemonic/focus relationship is explicit.

Set meaningful accessible metadata for controls that are otherwise ambiguous, especially:

- icon-only buttons
- custom widgets
- graphics/viewport controls
- non-text status indicators
- controls whose visible label is not sufficient for assistive technology

Do not use file names or internal object names as accessible labels.

Qt standard widgets already expose accessibility interfaces. Prefer them when they satisfy the interaction.

For custom widgets, determine whether to implement accessibility through `QAccessibleInterface`, usually via `QAccessibleWidget`, and send accessibility events when state/value changes.

Official references:
- https://doc.qt.io/qt-6/accessible.html
- https://doc.qt.io/qt-6/accessible-qwidget.html
- https://doc.qt.io/qt-6/qaccessible.html

## Color and visual communication

Do not rely on color alone for:

- errors
- warnings
- connection state
- selected state
- success/failure
- required fields

Pair color with text, iconography, shape, or another redundant cue.

Keep focus, selection, disabled, and error states distinguishable under platform themes, including dark/high-contrast modes when supported by the product.

## Font scaling and text resilience

Avoid assuming a fixed system font size. Test larger fonts and longer translations.

Prefer layouts over fixed geometry. Allow labels to grow or wrap where appropriate. Avoid clipping by using restrictive maximum sizes unless the design truly requires them.

## High DPI

Qt 6 uses device-independent geometry in higher-level GUI APIs and maps it to physical pixels according to the device pixel ratio.

Design implications:

- reason in logical/device-independent coordinates
- avoid custom calculations based on physical display pixels
- use `QIcon` and high-DPI capable image resources
- in custom painting, account for device pixel ratio only when manipulating raster backing stores or raw images
- test moving windows between monitors with different scaling factors
- test fractional scaling where supported

Official reference:
- https://doc.qt.io/qt-6/highdpi.html

## Localization

All user-facing text should be translatable unless it is truly data.

Design for:

- text expansion
- different word order
- longer button labels
- pluralization and numeric formatting
- date/time formats
- right-to-left layout when the product supports RTL languages

Avoid string concatenation that assumes English grammar. Keep labels and units semantically clear.

In `.ui` files, ordinary string properties are translatable by default. Use `notr="true"` only for content that should not be translated.

## Platform conventions

Do not manually reproduce platform differences that Qt can already handle.

Examples:

- use `QDialogButtonBox` for platform-appropriate dialog button ordering
- use `QKeySequence::StandardKey` for platform-appropriate standard shortcuts
- use native file dialogs through `QFileDialog` unless the product has a strong reason to disable them
- prefer standard Qt styles and `QStyle` metrics/icons for platform-adaptive behavior

When the product must have a uniform cross-platform brand, preserve platform interaction semantics even if appearance is customized.

## Testing matrix

For important UI changes, test at least:

- keyboard-only workflow
- default system font and enlarged font
- 100 percent and high-DPI scaling
- minimum supported window size
- large window/ultrawide behavior if relevant
- long translated strings or synthetic expansion
- light/dark/high-contrast themes where supported
- each target desktop platform
- empty, busy, error, and disabled states
