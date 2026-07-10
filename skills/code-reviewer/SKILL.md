---
name: code-reviewer
description: Review git diffs and commits — staged changes, unstaged changes, the full working tree, the last commit, a specific commit, or a commit range — and return a structured, findings-first report with proposed fixes. Use whenever the user asks to review code, review a diff, review staged/unstaged/working-tree changes, review a commit or commit range, do a code review, or asks for a security/performance/design/test review of recent changes — even if they don't say "code review" explicitly (e.g. "check this diff", "look over my changes", "any issues in this commit", "is this ready to merge", "review my branch against main"). Supports six selectable review scopes (design, correctness, maintainability, security, performance, tests), three effort levels (basic, standard, deep), and an interactive mode that asks up front what to review, in what scope, and how deep before starting — say "review interactively" or "guided review" to trigger it.
---

# Code Reviewer

Resolve `<SKILL_ROOT>` as the directory containing **this** skill's `SKILL.md`. Resolve
paths to `references/`, `scripts/`, and `assets/` from that directory.

A configurable, multi-scope code review workflow — deeper and more structured than a
quick diff skim, driven by three axes: **source** (what to review), **scope** (which
lenses to apply), and **effort** (how hard to look).

## Primary Directive

Your job is to review code changes, not to implement them.

Use a reviewer mindset. Prioritize bugs, regressions, design risks, security issues,
missing tests, and maintainability concerns over cosmetic nits. Findings are the primary
content of your response — don't bury them under process narration.

## How This Skill Is Configured

Every invocation resolves three independent inputs before any review work starts:

- **Source** — *what* to diff. Infer from context when possible; otherwise defaults to
  **staged changes** (`git diff --staged`). Do not prompt unless the user explicitly
  wants a guided, interactive setup (see **Interactive Mode** below).
- **Scope** — *which* lenses to apply. Optional; defaults to all six scopes if
  unspecified.
- **Effort** — *how deep* to dig. Optional; defaults to `standard` if unspecified.

All three axes have safe defaults. Don't ask about any of them unless the user
explicitly wants a guided, interactive setup (see **Interactive Mode** below).

## Resolving The Source (Review Target)

| # | Target | Command |
|---|--------|---------|
| 1 | Staged changes | `git diff --staged` |
| 2 | Unstaged changes | `git diff` |
| 3 | All working tree changes | `git diff HEAD` (staged + unstaged vs HEAD), plus `git status --porcelain` to surface any new untracked files — `git diff` never shows untracked content |
| 4 | Last commit (HEAD) | `git show HEAD` (equivalently `git diff HEAD~1..HEAD`) |
| 5 | Specific commit | `git show <sha-or-ref>` |
| 6 | Range of commits | see below |

**Range of commits** is the one case beyond a single diff:

- Two-dot (`A..B`): every commit reachable from `B` but not `A` — use for "diff literally
  from A's tree to B's tree."
- Three-dot (`A...B`, or phrasing like "my branch vs main"): based on the merge-base, so
  commits made on the base branch after divergence don't pollute the diff — this is
  usually what people mean by "review my branch." Prefer `git diff A...B` for this case.
- "Last N commits": use `git diff HEAD~N..HEAD` for one cumulative diff, or if the user
  wants per-commit granularity, enumerate with `git log --oneline -n N` and review each
  via `git show <sha>`.
- If it's genuinely unclear which the user means, ask one line: "Do you want everything
  different between the two refs since they diverged (`A...B`), or a literal diff from
  A's tree to B's tree (`A..B`)?"

Once the target is resolved: inspect the patch first, then read surrounding code as
needed — impacted call sites and dependents, tests added/changed/missing, and whether the
change matches any intent implied by the current chat session.

**Resolution rule**: if the source is unspecified and cannot be inferred from context,
default to **staged changes** (`git diff --staged`) and proceed — state the assumed
target in the **Review Target** section of the output. Do not interrupt to ask unless
**Interactive Mode** is triggered.

When the user names a target explicitly, or context makes one clear (e.g. "review my
branch against main" → commit range; "look at the last commit" → HEAD), use that instead
of the default.

For **Interactive Mode** only, present this menu if the user hasn't already named a
target:

```
1. Staged changes
2. Unstaged changes
3. All changes (staged + unstaged working tree)
4. Last commit (HEAD)
5. Specific commit
6. Range of commits
```

- If they pick 5: ask for the commit SHA or ref.
- If they pick 6: ask "What's the range? Give me a base and tip (e.g. `main..my-branch`
  or `main...my-branch`), or tell me how many recent commits (e.g. 'last 5 commits')."

## Selecting Scope

Six selectable lenses. Full checklists live in
`<SKILL_ROOT>/references/scope-checklists.md` — read the relevant section(s) right before
running that scope's pass (at `deep` effort, the checklist bullets get pasted verbatim
into that scope's parallel pass prompt). Each scope's checklist opens with a short *how to
look* heuristic — apply it, don't just tick bullets. That file also has a **Conditional
Extensions** section: change-type-specific checks (new HTTP routes, migrations, dependency
bumps, UI changes, etc.) that fold into the relevant scope whenever the diff touches that
surface — consult it and apply any that match.

- `design` — architecture and design quality: layering, SOLID/DRY, abstraction levels,
  coupling/cohesion, interface design, extensibility, conflicts with existing patterns.
- `correctness` — logic errors and regression risk: edge cases, broken invariants, null
  handling, concurrency/race conditions, backward-compat regressions.
- `maintainability` — readability and long-term cost: naming, control flow, duplication,
  stale comments, code smells, deprecated usage.
- `security` — input validation, auth/authz, injection, crypto, secrets handling,
  dependency risk, config security.
- `performance` — algorithmic efficiency, query cost, memory/CPU, network calls, caching,
  async patterns, resource leaks.
- `tests` — coverage of important paths/edge cases, test quality, mock usage, isolation,
  missing tests for changed behavior.

**Scope & Intent Alignment always runs**, regardless of which of the six above are
selected — it's foundational context-gathering (does the change match what was asked, is
anything incomplete or off-scope), not a domain lens, so it's not itself a selectable
option. Its checklist is at the bottom of
`<SKILL_ROOT>/references/scope-checklists.md`.

**Default**: if the user doesn't name a scope, run all six — this matches the always-run
default that a full review implies. Do not prompt just because scope alone is
unspecified.

## Selecting Effort

Three tiers control both how much ground gets covered and how rigorously findings get
verified before being reported.

**`basic`** — One quick, combined pass across all selected scopes in a single read of the
diff — don't organize the pass by scope internally, just keep all selected lenses in mind
at once while skimming. Skip the formal verification step entirely; report what's
directly evident. Cap at **5** findings. Use this when the user explicitly asks for
"quick", "basic", or "just a quick look," or when the diff is small and low-risk.

**`standard`** (default when effort is unspecified) — Run the always-on Scope & Intent
Alignment check first, then one sequential pass per selected scope, keeping notes per
scope. Then run one lightweight self-verification step before reporting: reread the diff
for each candidate finding, drop anything not actually evidenced by it, and dedupe
findings that surfaced under more than one scope. Cap at **10** findings.

**`deep`** — Full rigor, using parallel scope passes when your environment supports them.
See **Deep Effort: Parallel Scope Passes** below and your tool wrapper for dispatch
mechanics. Four stages: per-scope passes → cross-scope dedup → adversarial verify pass →
final "sweep for gaps" pass. Cap at **15–20** findings.

If effort is unspecified, default to `standard`.

## Interactive Mode

Trigger phrases: "review interactively," "ask me first," "guided review," "walk me
through it," or equivalent. When triggered, ask about all three axes together in one
message — even overriding anything already stated, to confirm — before starting anything
else:

```
Let's set this up:
1. What should I review? (staged / unstaged / all changes / last commit / specific
   commit / commit range)
2. Which scopes? (design, correctness, maintainability, security, performance, tests —
   default: all six)
3. How deep? (basic / standard / deep — default: standard)
```

Outside of interactive mode, source, scope, and effort all default silently per the
rules above.

## Context Rules

Always use the active chat context when available.

If this review is requested inside an existing chat session, use the current conversation
history to sharpen the review by incorporating previously discussed requirements,
constraints, and acceptance criteria; earlier design decisions or tradeoff discussions;
known bugs, incidents, or regressions mentioned in chat; and the user's stated risk
tolerance, scope, or planned follow-up work.

Do not ignore the actual diff in favor of chat context. Chat context sharpens the review;
it does not replace direct inspection of the changes.

## Review Workflow

1. **Resolve source** — per the rules above; default to staged changes if it can't be
   determined.
2. **Resolve scope & effort** — defaults, or the interactive menu if triggered.
3. **Gather the diff and context** — run the resolved git command(s); read surrounding
   code, call sites, and existing tests as needed.
4. **Run the review**, branching by effort:
   - `basic`: one combined pass across selected scopes, no verify.
   - `standard`: Scope & Intent Alignment, then one pass per selected scope, then a
     lightweight verify.
   - `deep`: Scope & Intent Alignment (inline, by you — see next section for why), then
     parallel per-scope passes (or sequential if your tool has no parallel agents), then
     dedup, then adversarial verify, then a gap-sweep pass.
5. **Validate findings** (standard/deep) — verify each against the diff and surrounding
   code, prefer concrete evidence over speculation, distinguish confirmed issues from open
   questions, and dedupe across scopes.
6. **Assemble and return the Output Contract** below.

## Deep Effort: Parallel Scope Passes

This section applies only at `deep` effort.

**Why Scope & Intent Alignment stays with you, not as a 7th parallel pass**: it's shared
context every domain lens needs (what the change is trying to do, anything obviously
incomplete or off-scope). Computing it once and handing the summary to every scope pass
avoids independent, possibly-inconsistent guesses at intent — and keeps it distinct from
the six domain checklists, which are genuinely independent lenses that are safe (and
faster) to run in parallel.

**Dispatch**: run one independent pass per *selected* scope. When your environment
supports parallel subagents or background agents, launch all scope passes in a single turn;
otherwise run them sequentially but keep notes separate per scope. Read your **tool
wrapper** for environment-specific dispatch mechanics (Task tool, Claude subagents,
sequential Copilot passes, etc.).

**Scope-pass prompt template** — paste real content, not a pointer; parallel passes do
not have this SKILL.md loaded:

```
You are reviewing a code change through the "<scope>" lens only.

## The diff under review
<the full resolved diff, or exact instructions to reproduce it, e.g. "run
`git diff --staged` yourself in the repo at <cwd>">

## Context on intent (from a prior alignment pass)
<2-5 sentence summary: what the change appears to be trying to do, and any
drift/incompleteness already noticed>

## Your checklist for this scope
<the specific bullet list for this one scope, copied verbatim from
<SKILL_ROOT>/references/scope-checklists.md — paste the actual items, don't just refer
to the file; append any matching Conditional Extensions bullets for this scope>

## What to return
Read surrounding code as needed (call sites, related tests, existing
patterns) before flagging anything. Cap yourself at 6 candidates for this
scope.

Return each candidate as a markdown block with: Severity
(critical/important/suggestion), Location (file and line), What's wrong, Why it matters,
Proposed fix.
```

**Cross-scope reconciliation**: once all scope passes return, collect all per-scope finding
lists and dedupe by (file, overlapping line range, similar description). If two scopes
flag essentially the same underlying issue (e.g. `security` and `correctness` both flag
the same unvalidated input), merge into one finding, tag it with both scopes, and keep the
more severe rating.

**Verify pass**: for each deduped candidate, reread the exact diff hunk and surrounding
code yourself; assign CONFIRMED, PLAUSIBLE, or REFUTED. Be recall-biased — default to
PLAUSIBLE, not REFUTED, when genuinely unsure. Drop REFUTED findings.

**Sweep for gaps**: one final fresh read — don't reuse any scope pass's notes — looking
only for defect classes nothing above caught. Specifically check for: a guard clause dropped
during a move/extract refactor, a mutable default evaluated once instead of per-call, a
lock scope that shrank, asymmetric test setup/teardown, a flipped config default, or any
checklist bullet for a selected scope that a scope pass never addressed at all.

Cap the final merged, verified list at **15–20** findings.

## Output Contract

Return a code review report in chat after the review finishes. Findings-first; keep
process narration brief by comparison.

### Review Target

State exactly what was reviewed: target type, the resolved git command/ref(s), the effort
level used, and which scopes were covered.

### Findings

List confirmed findings first, ordered by severity. For each:

- Severity: `critical`, `important`, or `suggestion`
- Scope: `design`, `correctness`, `maintainability`, `security`, `performance`, `tests`,
  or `scope-intent-alignment`
- Location: file and line references when available
- What is wrong
- Why it matters
- Proposed fix, improvement, or resolution
- Verdict (`deep` effort only): `CONFIRMED` or `PLAUSIBLE`

### Open Questions Or Assumptions

Include only items that could materially change the review outcome.

### Scope Summary

One line per scope actually run: what it found, or "no issues found."

### Effort Used

Echo the effort tier, and note explicitly if the finding cap was hit (more lower-severity
issues likely exist but weren't surfaced).

### Overall Verdict

Concise summary of overall risk, merge readiness, and the most important next actions.

## Posting to GitHub

This skill produces the **review content** — findings, severity, and merge verdict — as an
in-chat report. It does not call `gh` or post to GitHub itself.

When the user asks to **post the review on GitHub** (or "submit review comments on the PR",
"REQUEST_CHANGES on GitHub", etc.) and the repo remote is GitHub:

1. Finish this skill's review workflow and return the full Output Contract first — unless
   findings from a prior run in the same session are already complete.
2. Hand off to **[github-guide](../github-guide/SKILL.md)** for delivery. Read its
   [review-post.md](../github-guide/references/review-post.md) reference and map each
   finding per the **Handoff from code-reviewer** section in
   [github-guide](../github-guide/SKILL.md) (full verdict table):
   - `critical` → `**critical (blocking):**` prefix; `REQUEST_CHANGES` when reviewing
     **someone else's** PR, `COMMENT` on **your own** PR (GitHub returns 422 otherwise)
   - `important` → `**important:**`; `suggestion` → `**suggestion:**`
   - file+line locations → inline `comments[]`; unanchored findings → summary body only
3. Confirm auth and PR number (`gh auth status`, `gh pr view`) before posting.

For a combined "review this PR and post on GitHub" request, run both skills in that order
— do not skip the in-chat report unless the user explicitly asks to post silently.

On non-GitHub hosts, say this handoff applies only to GitHub and suggest the host's own
tooling when available.

## Output Rules

- Findings must be the primary content of the response.
- Keep summaries brief compared with the findings section.
- Prefer concrete, actionable fixes over vague advice.
- Reference exact files and lines when practical.
- Call out missing tests explicitly when change risk warrants it.
- If no findings are discovered, say that explicitly and mention any residual risks or
  testing gaps.
- Do not rewrite or patch the code unless the user explicitly asks for that in a
  follow-up request — this skill only proposes fixes, it doesn't apply them.
- Posting findings to GitHub is a separate delivery step — see **Posting to GitHub** above
  and hand off to [github-guide](../github-guide/SKILL.md) when the user asks to submit
  the review on a GitHub-hosted repo.

## Companion Skills

| Task | Path |
| --- | --- |
| Pre-review correctness audit | [../implementation-auditor/SKILL.md](../implementation-auditor/SKILL.md) |
| Post review to GitHub (`gh api`, inline comments, resolve threads) | [../github-guide/SKILL.md](../github-guide/SKILL.md) |
| PR description, sizing, self-review | [../pull-request-guide/SKILL.md](../pull-request-guide/SKILL.md) |
| Commit, push, rebase, worktrees | [../git-guide/SKILL.md](../git-guide/SKILL.md) |

## Resources

`<SKILL_ROOT>/references/scope-checklists.md` has the full bullet list per scope — read it
before running any scope's pass, and required verbatim in parallel pass prompts at `deep`
effort.
