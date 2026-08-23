# Implementation Report Template

Use this structure for the final response after executing an implementation plan. Keep it concise but specific enough for testing, debugging, and review.

```markdown
## Implementation Report

### Summary
- Implemented: <brief outcome>
- Status: <complete | partially complete | blocked>
- Branch: <current branch>
- Parallelization: <none | agent-runner used with N units in M waves | sequential fallback>

### Execution Units
| Unit | Mode | Scope | Status | Verification |
|---|---|---|---|---|
| <id> | <subagent/direct> | <files/modules> | <done/partial/blocked> | <pass/fail/skipped> |

### Files Changed
- `<path>`: <why it changed>
- `<path>`: <why it changed>

### Behavior and Interface Changes
- <runtime behavior/API/config/schema/test behavior change, or "none identified">

### Verification Performed
| Command | Result | Notes |
|---|---|---|
| `<command>` | <pass/fail/skipped> | <important output or reason> |

### Assumptions
- <assumption made to avoid blocking, or "none">

### Known Issues / Risks
- <risk, failing check, or "none known">

### Suggested Review Focus
- <files or logic the reviewer should inspect first>

### Suggested Follow-Up Testing
- <manual or broader automated checks that would increase confidence>
```

## Reporting Rules

- Include failed and skipped verification honestly.
- Include out-of-scope changes only if they were necessary and explain why.
- Prefer exact command names and high-signal failure messages over long logs.
- Do not claim the full suite passed unless it was actually run and passed.
- If subagents were used, summarize each subagent's contribution and verification outcome.
