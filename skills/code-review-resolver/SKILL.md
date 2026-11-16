---
name: code-review-resolver
description: "Use when resolving, fixing, or addressing code review findings classified as local — applying targeted code fixes only to the specific findings, running verification, and producing a fix report for re-review. Also classifies findings as upstream and emits backward handoff packets when the root cause traces to an earlier phase. Triggers on prompts to fix review findings, resolve code review issues, address review comments, or apply review fixes — even when the user doesn't say 'code review resolver'. Does not trigger on code review itself (code-reviewer), plan execution (plan-executor), debugging a reproducible defect (debugging-guide), or git commit (git-commit)."
---

# Code Review Resolver

Resolve `<SKILL_ROOT>` as the directory containing **this** skill's `SKILL.md`. Resolve
paths to `references/` from that directory.

Use this skill to resolve code review findings by applying targeted fixes to the specific
findings reported, then producing a fix report for re-review by [../code-reviewer/SKILL.md](../code-reviewer/SKILL.md).

## Primary Directive

Your job is to **resolve code review findings with surgical, scope-disciplined fixes**, not
to review code, refactor opportunistically, expand scope, or commit changes. Every fix must
trace directly to a specific finding id. When a finding's root cause traces to an earlier
phase (research, plan, or implement), do not patch it locally — emit a backward handoff
packet instead.

## When NOT to Use

- **Reviewing code or diffs** — use [../code-reviewer/SKILL.md](../code-reviewer/SKILL.md)
- **Executing an implementation plan** — use [../plan-executor/SKILL.md](../plan-executor/SKILL.md)
- **Debugging a reproducible defect with unknown root cause** — use
  [../debugging-guide/SKILL.md](../debugging-guide/SKILL.md)
- **Committing changes** — use [../git-guide/SKILL.md](../git-guide/SKILL.md) or the
  `/git-commit` command
- **Auditing an implementation for requirement coverage** — use
  [../implementation-auditor/SKILL.md](../implementation-auditor/SKILL.md)
- **Authoring or repairing an implementation plan** — use [../plan-guide/SKILL.md](../plan-guide/SKILL.md)

**Boundary vs debugging-guide:** if a fix attempt reveals a defect with an unclear root
cause, switch to [../debugging-guide/SKILL.md](../debugging-guide/SKILL.md) to prove root
cause before continuing.

## Rules

Non-negotiable; violating them produces unreviewable diffs and breaks the review loop:

1. **Every changed line traces to a finding id.** If a line was changed and no finding
   covers it, the change is out of scope.
2. **No opportunistic changes.** Do not refactor, rename, reformat, or "improve" code not
   flagged by a finding; note unrelated issues in the fix report instead of fixing them.
3. **No scope expansion.** If fixing a finding reveals the issue is larger than the finding
   suggests, mark the finding `unresolved` with the larger issue noted and let code-reviewer
   re-review with the new context.
4. **Match existing style.** Match the surrounding code's conventions; do not introduce
   new patterns.
5. **No commits.** This skill does not commit, push, stage, or deploy. Hand off to
   code-reviewer for re-review, then to git-guide or `/git-commit`.
6. **Surface failures.** Run verification after each fix or batch, record ambiguities and
   failures in the fix report, and never hide a scope violation in a long diff.

## Workflow

### 1. Parse the findings

Read the code review report. For each finding, extract the finding id (e.g., `cr-001`),
severity (`blocker`, `major`, `minor`), `root-cause-phase` (`local`, `research`, `plan`,
`implement`), location, scope, what is wrong, why it matters, and the proposed fix.
Separate findings into **local findings** (`root-cause-phase: local` — resolve with code
fixes) and **upstream findings** (`research`/`plan`/`implement` — do not fix; emit a
backward handoff packet for each).

### 2. Route upstream findings

For each upstream finding, create a backward handoff packet following the canonical
format in [../dev-workflow-orchestrator/references/backward-handoff-format.md](../dev-workflow-orchestrator/references/backward-handoff-format.md).
From phase: code-review; To: the finding's `root-cause-phase`; carry the finding id and
severity. Write each packet to `back-code-review-to-<target-phase>-<n>.md` in the run
directory. Do not attempt a local fix for an upstream finding. A local patch for a systemic
problem creates technical debt and hides the root cause.

### 3. Plan and apply local fixes

Group related findings that touch the same file or module. Fix blockers first, then
majors, then minors (or defer minors if the user or reviewer indicated they are optional).
For each fix, identify the exact file and location, the minimal change that resolves the
finding, the verification command, and whether a test must be added or updated. If a
finding is ambiguous — unclear location, open-ended required fix, or contradicting the
codebase — do not guess; mark it `unresolved` in the fix report with the reason.

Apply fixes one at a time or in small related batches: make the minimal change, update or
add the test if the finding is about missing or wrong tests, run the finding's verification
command or the project's focused test/build/lint for the touched area, and record the
result. If a fix attempt fails — the fix doesn't resolve the finding, a test breaks
unexpectedly, or a deeper issue appears — stop fixing that finding. Switch to
[../debugging-guide/SKILL.md](../debugging-guide/SKILL.md) if the root cause is unclear,
or mark the finding `unresolved` with the failure reason in the fix report.

### 4. Verify

After all local fixes, run the project's focused test/build/lint for all touched areas and
the broader regression suite if the changes could affect other areas. Confirm every fix's
verification command passes and no unrelated tests broke. If verification fails, do not
commit or proceed. Record the failure in the fix report and return to code-reviewer with
the failure visible.

### 5. Produce the fix report

Write the fix report using [references/fix-report-template.md](references/fix-report-template.md)
as the default structure, covering every finding id with a disposition
(`fixed`/`unresolved`/`deferred`/`upstream`), verification evidence, and backward handoff
packet paths for upstream findings. Do not create a report file in the repository unless the
dev-workflow-orchestrator or user asks for one at a specific path; otherwise provide the
report in the response or at the path the orchestrator specifies.

## Re-review handoff contract

After producing the fix report, hand off to [../code-reviewer/SKILL.md](../code-reviewer/SKILL.md)
for re-review. The handoff provides:

- **Fix report path** (or in-chat content): the `41-fix-report.md` artifact or response.
- **Amended diff**: the working-tree diff after all local fixes (not the original diff).
- **Finding disposition**: which finding ids were `fixed`, `unresolved`, `deferred`, or
  `upstream` (with backward handoff packet paths for upstream findings).

What code-reviewer re-reviews: the **amended diff** (the cumulative changes including
fixes), not the original diff. code-reviewer treats this as a fresh review pass — it does
not assume prior findings are resolved; it verifies the fixes against the finding ids and
may raise new findings introduced by the fixes. The loop continues until code-reviewer
returns `ready to commit` or `ready with notes`, or the round cap is hit.
