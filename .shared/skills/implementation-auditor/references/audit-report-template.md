# Audit Report Template

Use this exact structure unless the user requested a different format.

```markdown
# Implementation Audit Report

## Verdict

<pass | pass with risks | blocked | fail> — <one-sentence reason grounded in evidence>

## Scope audited

- Request/plan: <brief description>
- Branch/state: <current branch if known; mention uncommitted/untracked files>
- Files reviewed: <key files or diff areas>

## Verification evidence

| Command | Purpose | Result | Notes |
|---|---|---|---|
| `<exact command>` | <focused/regression/build/lint> | <pass/fail/blocked> | <exit code, counts, key failure, or blocker> |

## Requirement coverage

| Requirement / behavior | Implementation evidence | Test evidence | Status |
|---|---|---|---|
| <requirement> | <file/function/logic> | <test/command/manual blocker> | <covered/gap/risk/fail> |

## Findings

### Defects

- <actionable defect with file/function and why it violates the requirement, or `none found`>

### Test gaps

- <critical/major/minor gap and why it matters, or `none identified`>

### Risks and assumptions

- <runtime/platform/data/concurrency/API risk, or `none identified`>

## Recommended next actions

1. <highest-value fix, test, or rerun step>
2. <next action>
3. <next action>

## Notes for implementor/debugging agent

- <minimal context needed to reproduce failures or continue work>
```

Verdict rules:

- `pass`: requirements are covered by code review and relevant tests/builds passed.
- `pass with risks`: core evidence passed, but limited environment, skipped tests, minor gaps, or low-confidence areas remain.
- `blocked`: audit cannot reach a correctness conclusion because required validation could not run.
- `fail`: implementation defect, failing relevant test, unmet requirement, or critical missing test evidence.

Next-action routing by verdict (state in "Recommended next actions"):

- `pass` -> code-reviewer for diff review, then delivery.
- `pass with risks` -> code-reviewer with the listed risks as review focus.
- `fail` -> plan-executor for missing behavior, or debugging-guide for a failure/regression; then re-audit.
- `blocked` -> resolve the missing environment/dependency and re-audit; do not proceed to delivery.
