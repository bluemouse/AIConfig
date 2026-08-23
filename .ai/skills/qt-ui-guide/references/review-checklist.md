# Qt Desktop UI Review Checklist

Use this for screenshots, mockups, `.ui` files, and C++ implementations. Report only material findings; do not dump the full checklist unless requested.

## Severity

- **Critical**: blocks a core task, risks destructive data loss, or makes an essential workflow inaccessible.
- **High**: causes frequent errors, severe confusion, or major inefficiency in a primary workflow.
- **Medium**: noticeable friction, inconsistency, scaling/accessibility weakness, or maintainability problem.
- **Low**: polish issue with limited workflow impact.

## Workflow and information architecture

- Is the primary user goal clear?
- Is the entry point discoverable?
- Is the primary action easy to find?
- Are related controls grouped by user concept?
- Are advanced/rare controls appropriately disclosed?
- Are frequent tasks shorter than rare tasks?
- Does navigation preserve context?
- Are destructive paths recoverable?

## Visual hierarchy

- Is there a clear primary/secondary hierarchy?
- Are labels attached to the right controls?
- Is spacing used consistently?
- Is dense information aligned for scanning?
- Are borders/group boxes used only when they add meaning?
- Are error/warning/success cues redundant beyond color?

## Interaction and states

- Is every action followed by feedback?
- Are loading, empty, error, disabled, dirty, and success states designed where relevant?
- Are defaults safe and useful?
- Are selection and multi-selection semantics clear?
- Are double-click, Enter, Delete, context menu, and drag/drop semantics intentional?
- Can long operations be cancelled when safe?
- Are errors specific and recoverable?

## Keyboard and accessibility

- Can the core workflow be completed with keyboard only?
- Is tab order logical?
- Is focus visible?
- Are standard shortcuts used where appropriate?
- Do labels have buddies where appropriate?
- Do icon-only/custom controls have accessible names?
- Is meaning available without color?
- Will standard widgets expose appropriate accessibility semantics?
- Do custom widgets need a `QAccessibleWidget` implementation?

## Qt layout and resizing

- Does every resizable form/central widget have a top-level layout?
- Are child controls managed by layouts rather than absolute geometry?
- Are size policies sensible?
- Are minimum/maximum/fixed sizes used only with a real reason?
- Do stretch factors match intended resizing?
- Would a splitter or dock widget better support expert resizing/customization?
- Does the layout survive larger fonts and longer strings?

## Qt component choices

- Is `QDialogButtonBox` used for standard dialog actions?
- Are reusable commands represented by `QAction`?
- Are standard shortcuts represented by `QKeySequence::StandardKey`?
- Is model/view used for non-trivial list/tree/table data?
- Are standard widgets preferred over custom-painted controls?
- Is a `QMainWindow` using its central widget, menu/toolbar/status/dock architecture appropriately?

## Code and `.ui` separation

- Is stable structure in `.ui` and behavior in C++?
- Is generated `ui_*.h` left untouched?
- Are dynamic state changes centralized and understandable?
- Are object names descriptive enough for code and tests?
- Are signal/slot connections easy to trace?
- Is business logic kept out of presentation code where practical?

## High DPI, localization, platform

- Are hard-coded physical pixel assumptions avoided?
- Are raster/icon assets high-DPI safe?
- Does the design accommodate text expansion?
- Are strings translatable and grammatically complete?
- Are platform-standard button orders/shortcuts delegated to Qt?
- Has the design been considered on each target OS/style?

## Review output

For each finding state:

1. Severity
2. Location or component
3. Observed problem
4. User impact
5. Recommended change
6. Qt implementation note, if relevant
