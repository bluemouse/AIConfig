# Code Review Principles

Foundational best practices for every `code-reviewer` invocation. Apply these before,
during, and after scope passes — they govern *how* to review, while
`scope-checklists.md` governs *what* to look for.

## Reviewer mindset

- **Review, do not implement** — propose fixes; do not patch unless the user explicitly
  asks in a follow-up.
- **Understand before judging** — infer intent from the diff, commit message, PR
  description, and chat context before flagging mismatches.
- **Correctness and safety first** — bugs, regressions, security, and missing tests beat
  formatting and naming nits.
- **Evidence over speculation** — every finding must point to a diff hunk, call path, or
  file you read; drop hypotheticals with no supporting code path (especially security).
- **Constructive and specific** — state what is wrong, why it matters, and a concrete fix
  or next step; avoid vague "consider refactoring" without a target.
- **Blockers vs improvements vs questions** — map to `critical`, `important`, and
  `suggestion`; use **Open questions** when ambiguity could change the verdict, not when
  you are guessing at a defect.
- **Respect scope** — flag accidental or unrelated changes; do not expand the review into
  unrequested redesign of code the diff did not touch.

## Context to gather first

Before scope passes, build enough context that findings are grounded in intent and project
norms:

1. **Change metadata** — commit message(s) for the reviewed range (`git log` on the
   range); if a PR is open, read title/body (`gh pr view` when `gh` is available).
2. **Project norms** — skim applicable guidance when present: `AGENTS.md`, `CONTRIBUTING`,
   `README` sections for the touched area, `.cursor/rules/` or tool-specific review rules
   (e.g. `.cursor/BUGBOT.md`), and established patterns in neighboring files.
3. **The patch** — resolved git diff plus untracked files per the chosen source target.
4. **Surrounding code** — call sites, dependents, config wiring, and tests for each
   meaningful change (not the whole repo).
5. **Automated checks (when feasible)** — run focused commands the project already uses
   (unit tests for touched modules, lint/typecheck on changed paths, build if cheap).
   Record commands and outcomes in the report; do not claim green CI you did not run.
   Skip or mark **blocked** when the environment lacks dependencies — do not invent
   results.

If metadata is missing (empty commit message, no PR description), note it as a **PR
hygiene** signal when it materially slows review — not as a standalone nit.

## What to prioritize

Work in this order within each chunk of the diff:

1. **Scope & intent alignment** — wrong/incomplete change, scope drift, debug or unrelated
   edits mixed in.
2. **Correctness** — logic, edge cases, concurrency, error paths, backward compatibility.
3. **Security** — untrusted input to sensitive sinks, auth/authz on new entry points,
   secrets in diff.
4. **Tests** — behavior changed without a failing test that would catch regression.
5. **Design & maintainability** — only where the change introduces real coupling, API
   confusion, or long-term cost.
6. **Performance** — only on plausibly hot or unbounded paths.

Do not exhaust the finding cap on style preferences, formatting, or renames the codebase
already uses inconsistently elsewhere.

## Finding quality bar

A reportable finding must include:

| Field | Bar |
|-------|-----|
| Severity | Justified: `critical` = should block merge; `important` = should fix soon; `suggestion` = optional improvement |
| Location | `path:line` when possible; `unanchored` only when the issue is cross-cutting |
| Evidence | Grounded in the diff or a file you read for this review |
| Impact | Concrete failure mode, regression, or operational risk — not personal taste |
| Proposed fix | Actionable next step (code direction, test to add, doc to update) |

**Do not report:**

- Pure formatting unless it violates an documented project rule you cited.
- Hypothetical attacks with no reachable path in the changed code.
- Issues in unchanged code the diff did not worsen (unless the change relies on that
  broken assumption — then tie the finding to the new call site).
- Duplicate findings across scopes — merge and keep the higher severity.

**Prefer questions over faux-findings** when intent is unclear but no defect is evidenced.

## Constructive feedback

- Explain **why** the issue matters (user impact, data loss, incident class, maintenance
  cost).
- Prefer **one merged finding** over three comments on the same root cause.
- For design disagreements at `important` or below, describe the tradeoff and a minimal
  alternative — do not demand a full rewrite unless `critical`.
- When something is done well (clear test, good error handling, sensible abstraction),
  note it briefly in **What went well** — only when substantive; skip empty praise.

## PR and change hygiene signals

Flag (usually as `suggestion` or open questions) when the change makes review harder:

- Diff too large or mixed concerns (refactor + behavior + formatting) — suggest
  [pull-request-guide](../../pull-request-guide/SKILL.md) for split/self-review.
- Missing or misleading commit message / PR description vs actual diff.
- Public API or behavior change without doc/README update.
- High-risk surface (auth, migration, dependency bump) without tests or rollback notes.
- Leftover debug logging, commented-out code, or unrelated file churn.

These are reviewability issues, not substitutes for defect findings.

## After findings

- Route fixes per parent skill **Routing Findings Back**.
- Recommend re-running this skill on the amended diff before merge or GitHub posting.
- When posting to GitHub, hand off to [github-guide](../../github-guide/SKILL.md) — one
  summary, anchored inline comments, appropriate `REQUEST_CHANGES` / `COMMENT` event.
