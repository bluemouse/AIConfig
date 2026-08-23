# Desktop UI/UX Design Principles

Use this reference for framework-independent reasoning. Apply the Qt mapping from `qt-widgets-patterns.md` after the workflow and interaction model are sound.

## 1. Start from the user's task

Describe the user's goal before describing controls. Optimize the complete path from intent to completion, not one screen in isolation.

For each important workflow, identify:

- trigger or entry point
- information needed to decide
- primary action
- feedback after the action
- common error paths
- recovery or undo
- what context should be preserved

A visually clean panel can still be poor UX if users cannot find the next step or repeatedly lose context.

## 2. Make visual hierarchy obvious

Use size, spacing, alignment, grouping, typography, and contrast to communicate importance and relationships.

Rules of thumb:

- Give the primary action more prominence than secondary actions.
- Keep labels visually attached to the controls they describe.
- Use whitespace before adding borders or group boxes.
- Avoid giving every section equal visual weight.
- Keep repeated structures aligned.

The interface should remain understandable in grayscale and without decorative styling.

## 3. Prefer recognition over recall

Expose choices, history, examples, defaults, current state, and contextual actions when practical. Avoid making users remember command syntax, hidden modes, or previous values.

Useful patterns include menus, recent items, autocomplete, visible selections, descriptive labels, previews, and contextual affordances.

## 4. Use familiar controls and affordances

Choose a control whose behavior matches the user's expectation:

- push button: immediate action
- checkbox: independent boolean choice
- radio group: one choice from a small visible set
- combo box: one choice from a longer set
- slider: approximate or continuous range
- spin box: precise bounded numeric value
- tab: peer views that users switch between
- tree: hierarchical navigation or content
- table: comparable structured records

Do not create a custom control only to look unique.

## 5. Give immediate and proportional feedback

Every user action should visibly change state, start work, or explain why it cannot proceed.

For operations with noticeable duration:

- show busy or progress state
- disable only actions that truly conflict
- keep cancellation when feasible
- show completion or failure
- preserve the user's context

Avoid silent clicks and ambiguous disabled states.

## 6. Maintain consistency

Keep terminology, interaction semantics, icon meaning, shortcut behavior, spacing rules, and component behavior consistent.

Prefer external consistency with the operating system for common desktop conventions. Internal consistency should not be used to justify a non-standard behavior that repeatedly surprises users.

## 7. Prevent errors and make recovery cheap

Use this order:

1. prevent invalid actions when possible
2. detect mistakes early
3. explain the problem in user language
4. offer a direct recovery path
5. support undo for reversible destructive actions

Use confirmation dialogs primarily for destructive, consequential actions that are difficult to reverse. Do not confirm every routine action.

## 8. Minimize cognitive load without hiding necessary power

Desktop tools may be dense. The goal is not minimal content; the goal is understandable complexity.

Use progressive disclosure for advanced settings. Keep common settings visible and place rare technical options behind expandable sections, advanced dialogs, or context-specific panels.

Group by user concept rather than by implementation subsystem when those differ.

## 9. Optimize frequent workflows

Frequent actions should have shorter paths than rare actions. Support multiple access paths when useful:

- menu for discoverability
- toolbar for frequent pointer use
- shortcut for expert use
- context menu for local actions

Do not duplicate commands with inconsistent names or state.

## 10. Respect pointer and motor constraints

Frequently used targets should be easy to acquire. Avoid tiny icon-only targets, excessive pointer travel, and densely packed destructive actions.

Keep controls close to the information they affect. Separate dangerous actions from routine actions.

## 11. Group by meaning

Use proximity, alignment, similarity, and containment deliberately. Users infer relationships from layout before reading labels.

Prefer a small number of strong groups over many nested boxes.

## 12. Preserve context

When users navigate or refresh data, preserve meaningful state when possible:

- selection
- scroll position
- expanded tree nodes
- splitter positions
- dock visibility and placement
- active document/tab
- search query and filters
- viewport/camera position for visual tools

Unexpected state loss is especially costly in expert desktop applications.

## 13. Design all relevant states

Do not design only the ideal populated screen. Consider:

- first run
- loading/busy
- empty
- normal
- selected/focused/hovered
- disabled
- validation error
- operation failure
- partial availability
- dirty/unsaved
- success

The user should understand what happened and what to do next in each state.

## 14. Use clear language

Labels are interaction design.

Prefer concrete verbs and nouns:

- "Delete object" rather than "Perform deletion"
- "Could not open scene.obj" rather than "An unexpected error occurred"

State what happened, why when known, and the recovery action.

## 15. Evaluate the complete interaction loop

For each task, verify:

User intent -> find control -> act -> observe response -> understand result -> continue

If any transition is ambiguous, the design has an interaction problem even if every individual control looks correct.
