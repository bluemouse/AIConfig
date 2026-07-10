# Execution Unit Task Packet Template

Use this template when dispatching a unit to a subagent through [../../agent-runner/SKILL.md](../../agent-runner/SKILL.md) or an equivalent platform subagent primitive.

Packets dispatched via `agent-runner` must satisfy both this template and the return contract in [../../agent-runner/references/task-packet.md](../../agent-runner/references/task-packet.md).

```markdown
You are implementing one isolated unit from an implementation plan.

## Unit ID
<unit-id>

## Objective
<one-sentence objective>

## Plan context
<only the relevant plan excerpt and any parent assumptions needed for this unit>

## Repository context
- Current branch: <branch-name or "current branch">
- Do not create, switch, or rename branches.
- Do not commit, push, deploy, or run destructive commands.
- Preserve unrelated existing changes.

## File ownership
You may edit:
- <file/module/glob>

Do not edit:
- <files/modules owned by other units>
- <generated/vendor/lock files unless explicitly listed>

If you need an out-of-scope edit, stop and report the need instead of making it.

## Implementation constraints
- Follow existing project conventions.
- Make the smallest change that satisfies the plan.
- Avoid unrelated refactors, formatting churn, or dependency changes.
- Keep public API/behavior changes limited to what the plan requires.

## Verification
Run, if available:
- <targeted command>
- <additional command>

If a command cannot run, report the exact reason.

## Return format
Return exactly:
Status: completed | blocked | failed
Findings: <concise summary>
Changes: <files and summary>
Verification: <commands and outcomes>
Risks: <assumptions, conflicts, or follow-up>
```

## Dispatch Checklist

Before dispatching, confirm:

- The unit has no write overlap with another concurrent unit.
- The unit does not require results from a later unit.
- The task packet contains all context needed without relying on parent chat history.
- The expected output is structured enough for integration and reporting.
- The `Status` field uses `completed`, `blocked`, or `failed` so the parent can integrate per `agent-runner` rules.
