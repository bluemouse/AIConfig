# Debugging Report Template

Use this exact compact structure at the end of a debugging task.

```markdown
# Debugging Report: [short bug name]

## Status
[fixed | partially fixed | root cause found, not fixed | not reproduced | blocked]

## Bug Summary
- Expected: [behavior]
- Actual: [behavior]
- Impact: [scope/user-visible effect]
- Reproduction: `[exact command or steps]`

## Root Cause
[One precise paragraph explaining the earliest incorrect transition that caused the bug.]

## Evidence
- [fact from error/log/test/code path]
- [fact from instrumentation/comparison/trace]
- [fact that rules out an alternative cause]

## Experiments
| Hypothesis | Experiment | Outcome |
| --- | --- | --- |
| [hypothesis] | `[command/inspection]` | [confirmed/rejected + result] |

## Fix
- Changed files: [files]
- Production change: [minimal fix summary]
- Test/reproducer change: [regression test or durable reproducer summary]
- Why this fixes the root cause: [brief explanation]

## Verification
| Command | Result | Notes |
| --- | --- | --- |
| `[command]` | pass/fail/not run | [important output or reason] |

## Residual Risk and Follow-up
- [unverified area, remaining risk, or none]
```

Report rules:

- Keep the root cause specific. Avoid generic labels without mechanism.
- Include exact commands, not paraphrases.
- Include evidence that ruled out at least one plausible alternative when available.
- Mark anything not run as `not run` with a reason.
- Do not claim fixed unless targeted verification passed, or the limitation is explicit.
