---
name: code-review-plus
description: Review git diffs and commits — staged changes, unstaged changes, the full working tree, the last commit, a specific commit, or a commit range — and return a structured, findings-first report with proposed fixes. Use whenever the user asks to review code, review a diff, review staged/unstaged/working-tree changes, review a commit or commit range, do a code review, or asks for a security/performance/design/test review of recent changes — even if they don't say "code review" explicitly (e.g. "check this diff", "look over my changes", "any issues in this commit", "is this ready to merge", "review my branch against main"). Supports six selectable review scopes (design, correctness, maintainability, security, performance, tests), three effort levels (basic, standard, deep), and an interactive mode that asks up front what to review, in what scope, and how deep before starting — say "review interactively" or "guided review" to trigger it.
---

# Code Review++

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

- **Source** — *what* to diff. Required. If it can't be determined, always ask before
  proceeding — guessing wrong here wastes the entire review.
- **Scope** — *which* lenses to apply. Optional; defaults to all six scopes if
  unspecified. Never blocks on its own — only a missing source forces a question.
- **Effort** — *how deep* to dig. Optional; defaults to `standard` if unspecified.

This resolution is intentionally asymmetric: getting the source wrong invalidates the
whole review, so it's the one thing worth interrupting for. Scope and effort have safe,
useful defaults, so don't ask about them unless the user explicitly wants a guided,
interactive setup (see **Interactive Mode** below).

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
always ask before doing anything else. Present this menu:

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

Six selectable lenses. Full checklists live in `references/scope-checklists.md` — read
the relevant section(s) right before running that scope's pass (at `deep` effort, paste
the checklist bullets verbatim into that scope's subagent prompt).

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
option. Its checklist is at the bottom of `references/scope-checklists.md`.

**Default**: if the user doesn't name a scope, run all six — this matches the always-run
default that a full review implies. Do not prompt just because scope alone is
unspecified; only a missing source forces a question.

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

**`deep`** — Full rigor, using parallel subagents. See **Deep Effort: Parallel Subagent
Dispatch** below for the complete procedure. Four stages: per-scope subagent dispatch →
cross-scope dedup → adversarial verify pass → final "sweep for gaps" pass. Cap at
**15–20** findings.

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

Outside of interactive mode, only the source is gated behind a mandatory question; scope
and effort default silently per the rules above.

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

1. **Resolve source** — per the rules above; ask if it can't be determined.
2. **Resolve scope & effort** — defaults, or the interactive menu if triggered.
3. **Gather the diff and context** — run the resolved git command(s); read surrounding
   code, call sites, and existing tests as needed.
4. **Run the review**, branching by effort:
  - `basic`: one combined pass across selected scopes, no verify.
  - `standard`: Scope & Intent Alignment, then one pass per selected scope, then a
    lightweight verify.
  - `deep`: Scope & Intent Alignment (inline, by you), then parallel per-scope
    subagent dispatch, then dedup, then adversarial verify, then a gap-sweep pass.
5. **Validate findings** (standard/deep) — verify each against the diff and surrounding
   code, prefer concrete evidence over speculation, distinguish confirmed issues from open
   questions, and dedupe across scopes.
6. **Assemble and return the Output Contract** below.

## Deep Effort: Parallel Subagent Dispatch

This section applies only at `deep` effort.

**Why Scope & Intent Alignment stays with you, not as a 7th subagent**: it's shared
context every domain lens needs (what the change is trying to do, anything obviously
incomplete or off-scope). Computing it once and handing the summary to every subagent
avoids six independent, possibly-inconsistent guesses at intent — and keeps it distinct
from the six domain checklists, which are genuinely independent lenses that are safe (and
faster) to run in parallel.

**Prepare before dispatch**: read `references/scope-checklists.md` for every selected
scope now — you will paste each scope's bullets verbatim into that scope's subagent
prompt. Subagents do not automatically load this skill or its reference file.

**Diff handoff**: the parent reviewer must resolve the source and gather the review
material before dispatching subagents. Run the resolved git command(s) yourself, collect
the exact diff to review, and include any untracked file paths and contents that matter.
Do not assume subagents can run terminal or git commands. For very large patches, prefer
passing only the relevant hunks plus explicit file paths and a concise summary of the
omitted context, rather than asking subagents to reconstruct the diff themselves. Treat
the patch as very large if the resolved diff exceeds about 800 lines or would consume
more than roughly 40% of the subagent prompt budget.

**Dispatch**: in a single message, issue one `runSubagent` tool call per *selected*
scope, all in parallel (multiple tool calls in one turn, not sequential calls). Use the
platform's parallel tool wrapper when available so the scopes actually launch together;
otherwise, fall back to sequential dispatch and state that explicitly in the `Effort
Used` section of the final review output. Use the
`Explore` agent for each scope because it is optimized for read-only codebase inspection.
Set a short description like `Code review: <scope> scope`, and make the prompt explicitly
forbid edits or destructive commands.

**Subagent prompt template** — paste real content, not a pointer; the subagent does not
have this SKILL.md loaded:

```
You are reviewing a code change through the "<scope>" lens only.

Do not edit files, apply patches, or run destructive commands. Read-only review only.

## Repository
<absolute path to repo root>

## The diff under review
<the review material prepared by the parent reviewer: the full resolved diff if small,
or the relevant hunks plus file paths and a short summary if the patch is large. If
untracked files are in scope, list their paths and paste the relevant contents. Do not
tell the subagent to reproduce the diff from git commands.>

## Context on intent (from a prior alignment pass)
<2-5 sentence summary: what the change appears to be trying to do, and any
drift/incompleteness already noticed>

## Your checklist for this scope
<the specific bullet list for this one scope, copied verbatim from
references/scope-checklists.md — paste the actual items, don't just refer
to the file>

## What to return
Read surrounding code as needed (call sites, related tests, existing patterns) before
flagging anything. Cap yourself at 6 candidates for this scope.

In your final message, return each candidate as a markdown block with:
- Severity (critical/important/suggestion)
- Scope: "<scope>"
- Location (file and line)
- What's wrong
- Why it matters
- Proposed fix
- Failure scenario (concrete example of how this could break)

Do not assign a final verdict (CONFIRMED/PLAUSIBLE/REFUTED) — that happens in a separate
verification pass you are not doing.
```

**Cross-scope reconciliation**: once all subagents return, collect findings from each
subagent's final message and dedupe by (file, overlapping line range, similar
description). If two scopes flag essentially the same underlying issue (e.g. `security`
and `correctness` both flag the same unvalidated input), merge into one finding, tag it
with both scopes, and keep the more severe rating.

**Verify pass**: for each deduped candidate, reread the exact diff hunk and surrounding
code yourself; assign CONFIRMED, PLAUSIBLE, or REFUTED. Be recall-biased — default to
PLAUSIBLE, not REFUTED, when genuinely unsure. Drop REFUTED findings.

**Sweep for gaps**: one final fresh read — don't reuse any subagent's notes — looking only
for defect classes nothing above caught. Specifically check for: a guard clause dropped
during a move/extract refactor, a mutable default evaluated once instead of per-call, a
lock scope that shrank, asymmetric test setup/teardown, a flipped config default, or any
checklist bullet for a selected scope that its subagent never addressed at all.

**Retry and fallback**: if a scope subagent fails or returns unusable output, retry that
scope once with the same prompt. If it still fails, run that scope sequentially yourself
and continue with dedup/verify so `deep` effort still completes. If the patch is too
large to hand off cleanly, keep the parent reviewer responsible for narrowing the review
material before retrying or falling back.

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
- Posting findings as PR review comments is out of scope for this skill — if asked, say
  so.

## Resources

`references/scope-checklists.md` has the full bullet list per scope — read it before
running any scope's pass.
