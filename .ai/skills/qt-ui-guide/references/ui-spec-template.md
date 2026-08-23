# UI Specification Template

Use this for a new screen, dialog, panel, or substantial redesign. Omit sections that do not apply.

## 1. Purpose

- **Component/window:**
- **Primary user:**
- **Primary goal:**
- **Secondary goals:**
- **Out of scope:**

## 2. Entry and completion

- **Entry points:**
- **Successful completion:**
- **Cancel/close behavior:**
- **Unsaved/dirty behavior:**

## 3. Primary workflow

1. User...
2. System...
3. User...
4. System...

List alternate/error paths separately.

## 4. Information architecture

Describe the major regions in reading/interaction order.

Example:

- top: command/search area
- left: navigation tree
- center: primary editor/viewport
- right: inspector
- bottom: status/output

## 5. Qt widget hierarchy

Provide a compact tree with proposed object names.

Example:

```text
QDialog settingsDialog
`- QVBoxLayout mainLayout
   |- QTabWidget settingsTabs
   |  |- QWidget generalPage
   |  `- QWidget renderingPage
   `- QDialogButtonBox buttonBox
```

For each non-obvious widget, explain why it is the right control.

## 6. Layout and resizing contract

State:

- minimum useful window size if product requirements define one
- which regions expand
- stretch factors
- splitter/dock behavior
- scroll behavior
- what remains fixed only if truly necessary

Avoid pixel-perfect dimensions unless they are externally required.

## 7. Controls and behavior

Use a table or concise list with:

- object name
- visible label
- widget type
- default value/state
- enabled/visible conditions
- action on change/activation
- validation
- tooltip/help only when useful

## 8. Commands and shortcuts

List reusable commands as `QAction` candidates and specify `QKeySequence::StandardKey` where applicable.

## 9. States

Define relevant states:

- initial
- loading/busy
- empty
- normal
- disabled
- validation error
- operation error
- dirty/unsaved
- success

For each, state what changes visually and what actions remain possible.

## 10. Error and recovery model

Specify:

- preventable errors
- validation placement/message
- operation failure behavior
- undo/redo behavior
- destructive confirmation only when needed

## 11. Accessibility

Specify:

- focus order
- default/cancel behavior
- label buddies
- accessible names for icon-only/custom controls
- keyboard interaction for custom behaviors
- non-color status cues

## 12. Localization and high DPI

Specify constraints such as:

- translatable strings
- text expansion
- units
- RTL considerations
- scalable icons/images
- no fixed physical-pixel assumptions

## 13. C++ integration

State what belongs outside `.ui`:

- models
- signal/slot handlers
- validators
- async work
- state binding
- persistence
- dynamic content

## 14. Acceptance criteria

Write testable criteria, for example:

- User can complete the primary task with keyboard only.
- Resizing from the minimum supported size to a large window does not clip primary controls.
- Dialog action order follows the platform style.
- Invalid input is explained next to the affected field and focus can move directly to it.
- The generated `.ui` passes the bundled `.ui` validator and `uic` when available.
