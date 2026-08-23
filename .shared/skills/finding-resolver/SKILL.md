---
name: finding-resolver
description: "Use when resolving, fixing, or addressing code review findings classified as local — applying targeted code fixes only to the specific findings, running verification, and producing a fix report for re-review. Also classifies findings as upstream and emits backward handoff packets when the root cause traces to an earlier phase. Triggers on prompts to fix review findings, resolve code review issues, address review comments, or apply review fixes — even when the user doesn't say 'finding resolver'. Does not trigger on code review itself (code-reviewer), plan execution (plan-executor), debugging a reproducible defect (debugging-guide), or git commit (git-commit)."
---

# Finding Resolver

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

## When to Use

- Resolving code review findings classified as `root-cause-phase: local`
- Applying targeted fixes to specific findings from [../code-reviewer/SKILL.md](../code-reviewer/SKILL.md)
- Producing a fix report for re-review
- Classifying findings as upstream and emitting backward handoff packets when the root
  cause traces to research, plan, or implement phases

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

**Boundary vs plan-executor:** this skill resolves **review findings** — discrete,
finding-level issues with a specific location and required fix. [../plan-executor/SKILL.md](../plan-executor/SKILL.md)
executes **implementation plans** — ordered tasks with TDD specs and execution waves. A
review finding is not a plan task; forcing it into plan-executor's format loses the
finding's severity, location, and root-cause classification.

**Boundary vs debugging-guide:** this skill applies known fixes to specific findings. When
a fix attempt reveals a defect with an unclear root cause — a test fails unexpectedly, a
crash appears, or the fix doesn't resolve the finding — switch to
[../debugging-guide/SKILL.md](../debugging-guide/SKILL.md) to prove root cause before
continuing.

## Companion Skills

- Primary input from [../code-reviewer/SKILL.md](../code-reviewer/SKILL.md) — findings with
  `root-cause-phase` field
- After local fixes: return to [../code-reviewer/SKILL.md](../code-reviewer/SKILL.md) for
  re-review (the code review loop)
- When a fix attempt reveals a defect with unclear root cause:
  [../debugging-guide/SKILL.md](../debugging-guide/SKILL.md)
- When a finding is classified as upstream: emit a backward handoff packet to the target
  phase (research, plan, or implement)
- For git mechanics after re-review approves: [../git-guide/SKILL.md](../git-guide/SKILL.md)
  or the `/git-commit` command

## Operating posture

Default to a **surgical** posture: precise, minimal, and scope-disciplined.

Always:
- Fix only the specific findings reported. Every changed line must trace to a finding id.
- Do not expand scope. Do not refactor adjacent code, improve naming, fix unrelated issues,
  or make opportunistic changes — even if they seem helpful.
- Match existing project conventions over introducing new patterns.
- Run verification after each fix or batch of related fixes.
- Preserve the finding id throughout the fix so re-review can trace the change back to the
  finding.
- When a finding's root cause is genuinely upstream (the design decision, requirement, or
  plan is the cause, not the code), do not patch it locally. Emit a backward handoff packet.

## Workflow

### 1. Parse the findings

Read the code review report. For each finding, extract:

- Finding id (e.g., `cr-001`)
- Severity (`blocker`, `major`, `minor`, `note`)
- `root-cause-phase` field (`local`, `research`, `plan`, `implement`)
- Location (file, line range, symbol)
- Issue description
- Required fix or recommendation

Separate findings into two groups:

- **Local findings** (`root-cause-phase: local`): resolve these with code fixes.
- **Upstream findings** (`root-cause-phase: research | plan | implement`): do not fix
  these. Emit a backward handoff packet for each.

### 2. Classify and route upstream findings

For each upstream finding, create a backward handoff packet. The packet must follow the
backward handoff format defined by the dev-workflow-orchestrator. For each packet:

- `From phase`: code-review
- `To phase`: the `root-cause-phase` value
- `Source finding`: the finding id and severity
- `Root cause classification`: why this is not a local defect and why the target phase is
  the root
- `What the target phase must resolve`: the issue, why it matters, the required fix, and
  evidence
- `Context from the source phase`: what was attempted (if anything) and why local fix is
  insufficient

Write each packet to `back-review-to-<target-phase>-<n>.md` in the run directory.

Do not attempt a local fix for an upstream finding. A local patch for a systemic problem
creates technical debt and hides the root cause.

### 3. Plan the local fixes

For local findings, group related findings that touch the same file or module. Plan the
fix order:

1. Fix blockers first.
2. Fix majors next.
3. Fix minors and notes last (or defer them if the user or reviewer indicated they are
   optional).

For each fix, identify:

- The exact file and location to change.
- The minimal change that resolves the finding.
- The verification command to run after the fix.
- Whether the fix requires a new test or modifies an existing test.

If a finding is ambiguous — the location is unclear, the required fix is open-ended, or
the finding contradicts the codebase — do not guess. Mark the finding as `unresolved` in
the fix report with the reason, and let code-reviewer re-review with the ambiguity
visible.

### 4. Apply fixes

Apply fixes one at a time or in small related batches. For each fix:

1. Make the minimal change that resolves the finding.
2. Do not touch code outside the finding's scope.
3. If the fix requires a test change (the finding is about missing or wrong tests), update
   or add the test.
4. Run the finding's verification command or the project's focused test/build/lint for the
   touched area.
5. Record the result.

If a fix attempt fails — the fix doesn't resolve the finding, a test breaks unexpectedly,
or the change reveals a deeper issue — stop fixing that finding. Switch to
[../debugging-guide/SKILL.md](../debugging-guide/SKILL.md) if the root cause is unclear, or
mark the finding as `unresolved` with the failure reason in the fix report.

### 5. Verify

After all local fixes are applied:

- Run the project's focused test/build/lint for all touched areas.
- Run the broader regression suite if the changes could affect other areas.
- Confirm that every fix's verification command passes.
- Confirm that no unrelated tests broke.

If verification fails, do not commit or proceed. Record the failure in the fix report and
return to code-reviewer with the failure visible.

### 6. Produce the fix report

Write the fix report using [references/fix-report-template.md](references/fix-report-template.md)
as the default structure. The report must include:

- Run directory and source review report path.
- Summary: counts of findings resolved, unresolved, deferred, and routed upstream.
- Per-finding resolution: finding id, severity, resolution status (`fixed`, `unresolved`,
  `deferred`, `upstream`), what was changed, verification result.
- Upstream findings: list of backward handoff packets created, with target phase and
  finding id.
- Verification commands run and outcomes.
- Files changed and why (traced to finding ids).
- Risks, assumptions, and follow-up needs.
- Readiness for re-review: whether the fix report is ready for code-reviewer to re-review.

Do not create a report file in the repository unless the dev-workflow-orchestrator or user
asks for one at a specific path. Otherwise, provide the report in the response or at the
path the orchestrator specifies.

## Scope discipline rules

These rules are non-negotiable. Violating them produces unreviewable diffs and breaks the
code review loop.

1. **Every changed line traces to a finding id.** If a line was changed and no finding
   covers it, the change is out of scope.
2. **No opportunistic changes.** Do not refactor, rename, reformat, or "improve" code that
   was not flagged by a finding. If you notice an unrelated issue, mention it in the fix
   report — do not fix it.
3. **No scope expansion.** If fixing a finding reveals that the issue is larger than the
   finding suggests, do not expand the fix. Mark the finding as `unresolved` with the
   larger issue noted, and let code-reviewer re-review with the new context.
4. **Match existing style.** Even when fixing, match the surrounding code's conventions.
   Do not introduce new patterns.
5. **No commits.** This skill does not commit, push, stage, or deploy. Hand off to
   code-reviewer for re-review, then to git-guide or `/git-commit` for commit.

## Quality bar

A strong fix report:
- Traces every change to a specific finding id.
- Distinguishes fixed, unresolved, deferred, and upstream-routed findings.
- Shows verification evidence (commands run, outcomes).
- Surfaces ambiguities and failures instead of hiding them.
- Makes re-review straightforward for code-reviewer.
- Does not bury scope violations in a long diff.
