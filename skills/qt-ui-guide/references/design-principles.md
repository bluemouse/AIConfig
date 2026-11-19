# Design Principles

Priority order and review severity rubric for this skill. Design every relevant state: loading/busy, empty, disabled, validation error, operation failure, dirty/unsaved, success.

## Priority order

When principles conflict: (1) correct workflow and information architecture, (2) clear state, feedback, and error recovery, (3) keyboard access and accessibility, (4) platform conventions and familiar Qt controls, (5) resizing, high-DPI, and localization resilience, (6) consistency with the existing application, (7) visual polish. Do not optimize a single screen at the expense of the complete workflow.

## Review severity rubric

Rank findings by user impact:

- **Critical**: blocks a core task, risks destructive data loss, or makes an essential workflow inaccessible.
- **High**: causes frequent errors, severe confusion, or major inefficiency in a primary workflow.
- **Medium**: noticeable friction, inconsistency, scaling/accessibility weakness, or maintainability problem.
- **Low**: polish issue with limited workflow impact.
