# Code Review Report Template

Use this structure for the final in-chat review report. Adapt only when sections are
genuinely irrelevant. Findings are the primary content — keep summaries brief by
comparison.

```markdown
# Code Review Report

## 1. Review target

- Target: <staged | unstaged | working tree | last commit | specific commit | commit range | branch changes | natural-language fallback>
- Git command/ref(s): `<exact command or ref used>`
- Base ref (branch changes only): `<base ref and merge-base sha, or n/a>`
- Effort: <basic | standard | deep>
- Scopes run: <design, correctness, maintainability, security, performance, tests — list only those actually run>
- Intent summary: <1–3 sentences on what the change appears to be trying to do>
- Diff size: <approx lines changed, file count — or `n/a` for natural-language fallback>
- Coverage: <all changed files reviewed | partial — list reviewed vs deferred files, or `full`>

## 2. Automated checks (when run)

| Command | Purpose | Result | Notes |
|---------|---------|--------|-------|
| `<exact command or `none run`>` | <test/lint/build/typecheck> | <pass/fail/blocked/skipped> | <brief note> |

## 3. What went well

Optional — 0–3 substantive bullets only; omit the section if nothing notable.

- <good test coverage, clear error handling, sensible abstraction, etc.>

## 4. Findings

List confirmed findings first, ordered by severity (`critical` → `important` → `suggestion`).
If none were found, write `No findings.` and skip the table and detail subsections.

| id | severity | scope | location | issue | recommended route |
|----|----------|-------|----------|-------|-------------------|
| cr-001 | critical/important/suggestion | design/correctness/maintainability/security/performance/tests/scope-intent-alignment | `path:line` or unanchored | <short title> | direct edit / plan-executor / debugging-guide / plan-guide / test-driven-dev-guide / implementation-auditor |

### Finding details

#### cr-001: [short title]

- Severity: <critical | important | suggestion>
- Scope: <scope tag(s); comma-separate when merged from multiple scopes>
- Location: `<path:line>` or `unanchored`
- What is wrong: <concrete description grounded in the diff>
- Why it matters: <regression, security, maintainability, or merge-risk impact>
- Proposed fix: <actionable fix or improvement — not a vague suggestion>
- Verdict (deep effort only): <CONFIRMED | PLAUSIBLE — omit at basic/standard effort>
- Recommended route: <direct scoped edit | plan-executor | debugging-guide | plan-guide | test-driven-dev-guide | implementation-auditor>

## 5. Open questions or assumptions

Include only items that could materially change the review outcome.

- <question or assumption, or `none`>

## 6. Scope summary

One line per scope actually run:

| scope | result |
|-------|--------|
| scope-intent-alignment | <brief result or `no issues found`> |
| design | <brief result or `no issues found`> |
| correctness | <brief result or `no issues found`> |
| maintainability | <brief result or `no issues found`> |
| security | <brief result or `no issues found`> |
| performance | <brief result or `no issues found`> |
| tests | <brief result or `no issues found`> |

## 7. Effort used

- Tier: <basic | standard | deep>
- Finding cap: <5 | 10 | 15–20>
- Cap hit: <yes — lower-severity issues likely remain | no>
- Large-diff mode: <yes — partial file coverage; see Review target | no>

## 6. Overall verdict

- Merge readiness: <ready | ready with fixes | not ready>
- Risk summary: <one or two sentences on overall risk>
- Top next actions:
  1. <highest-priority fix or test>
  2. <next action>
  3. <next action if needed>
```

Rules:

- **Empty diff** — when git produces no changed hunks and there is nothing to review, do
  not emit this template; reply in one sentence per parent skill **Empty Or Blocked Diff**.
- Findings must be the largest section of the report.
- Order findings by severity, then by impact within the same severity.
- Use `critical` only for defects that should block merge (correctness bugs, security
  holes, data loss, broken invariants).
- Use `important` for material issues that should be fixed before or immediately after
  merge.
- Use `suggestion` for improvements that do not block merge.
- Every finding needs a concrete proposed fix when one exists — prefer specific code or
  test changes over generic advice.
- Reference exact files and lines when practical; mark `unanchored` when the issue spans
  the change or lacks a single line.
- At `deep` effort, include `Verdict: CONFIRMED | PLAUSIBLE` on each finding detail;
  omit the verdict field at `basic` or `standard` effort.
- When two scopes flag the same underlying issue, merge into one finding, tag all
  relevant scopes, and keep the more severe rating.
- If no findings are discovered, say so explicitly in section 2 and mention any residual
  risks or testing gaps in the overall verdict.
- Do not rewrite or patch code in the report unless the user explicitly asks — propose
  fixes only.
- State the recommended lifecycle route per finding when fixes are needed (see parent
  skill **Routing Findings Back**).
- When **large-diff mode** applied, never imply full-repo coverage — list deferred paths
  in **Review target → Coverage** and **Effort used → Large-diff mode**.
- For **natural-language fallback** (blocked git diff), set target accordingly and list
  files read instead of a unified diff command.

Severity → GitHub handoff (when posting via github-guide):

- `critical` → `**critical (blocking):**` prefix
- `important` → `**important:**` prefix
- `suggestion` → `**suggestion:**` prefix
- Anchored findings (`path:line`) → inline PR comments; unanchored → summary body only
