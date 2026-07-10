# Task packet template

Use this structure for every dispatched subagent.

```text
Role: You are an isolated subagent responsible only for the scope below.

Objective:
<one concrete outcome>

Context:
<relevant architecture, symptoms, errors, requirements, and repository instructions>

Scope:
- Read: <paths or sources>
- Write: <exclusive paths, or "none; read-only">

Constraints:
- Do not modify anything outside the write scope.
- Do not commit, merge, push, deploy, or change shared/global state.
- Preserve existing behavior outside the objective.
- Do not solve adjacent tasks assigned to other agents.

Procedure:
1. Inspect the specified context.
2. Identify the root cause or required change.
3. Implement only within scope, or produce a proposed patch if read-only.
4. Run: <targeted verification commands>.

Acceptance criteria:
- <observable criterion>
- <observable criterion>

Return exactly:
Status: completed | blocked | failed
Findings: <concise root cause or result>
Changes: <files and summary, or proposed patch>
Verification: <commands and outcomes>
Risks: <assumptions, conflicts, or follow-up>
```

## Packet checklist

Before dispatch, confirm that the packet:

- names one problem domain
- contains enough context without parent-history dependence
- defines exclusive write ownership
- states non-goals and destructive-action restrictions
- includes an executable verification method
- asks for structured evidence rather than confidence

For research tasks, replace file scope with explicit sources or questions and require citations or evidence locations. For review tasks, mark the packet read-only and prohibit applying fixes.
