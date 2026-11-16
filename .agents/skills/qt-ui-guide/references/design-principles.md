# Desktop UI/UX Design Principles

Framework-independent design reasoning for this skill. Apply the Qt mapping in `qt-widgets-patterns.md` after the workflow and interaction model is sound.

Reason from the user's task first: entry point, information needed to decide, primary action, feedback, error paths, recovery/undo, and context worth preserving. Prefer familiar controls, give immediate and proportional feedback, prevent errors before confirming them (confirm only hard-to-reverse destructive actions), keep frequent workflows shorter than rare ones, group by user concept, use clear concrete language, and design every relevant state (loading/busy, empty, disabled, validation error, operation failure, dirty/unsaved, success). Preserve user context — selection, scroll, expansion, splitters, docks, active tab — across navigation. Verify the complete loop: intent -> find control -> act -> observe response -> understand result -> continue. If any transition is ambiguous, the design has an interaction problem even if every control looks correct.

## Priority order

When principles conflict: (1) correct workflow and information architecture, (2) clear state, feedback, and error recovery, (3) keyboard access and accessibility, (4) platform conventions and familiar Qt controls, (5) resizing, high-DPI, and localization resilience, (6) consistency with the existing application, (7) visual polish. Do not optimize a single screen at the expense of the complete workflow.

## Review severity rubric

Rank findings by user impact:

- **Critical**: blocks a core task, risks destructive data loss, or makes an essential workflow inaccessible.
- **High**: causes frequent errors, severe confusion, or major inefficiency in a primary workflow.
- **Medium**: noticeable friction, inconsistency, scaling/accessibility weakness, or maintainability problem.
- **Low**: polish issue with limited workflow impact.
