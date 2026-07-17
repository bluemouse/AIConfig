---
name: code-reviewer
description: Review git diffs and commits — staged changes, unstaged changes, branch changes (pre-push vs default branch), the full working tree, the last commit, a specific commit, or a commit range — and return a structured, findings-first report with proposed fixes. Use whenever the user asks to review code, review a diff, review staged/unstaged/working-tree/branch changes, review a commit or commit range, do a code review, or asks for a security/performance/design/test review of recent changes — even if they don't say "code review" explicitly (e.g. "check this diff", "look over my changes", "any issues before I push", "is this ready to merge", "review my branch against main"). Supports six selectable review scopes (design, correctness, maintainability, security, performance, tests), three effort levels (basic, standard, deep), and an interactive mode that asks up front what to review, in what scope, and how deep before starting — say "review interactively" or "guided review" to trigger it.
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

Follow `<SKILL_ROOT>/references/review-principles.md` for reviewer mindset, context
gathering, finding quality, constructive feedback, and PR hygiene — it is mandatory for
every review, not optional depth reading.

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
| 7 | Branch changes (pre-push) | see below |

**Branch changes (pre-push)** — everything on the current branch since it diverged from a
base ref, **plus** all local uncommitted edits (staged and unstaged). This is the usual
"review before I push" or "review my branch" target.

1. Resolve `<base>`: use a base the user named (e.g. `main`); otherwise infer the repo's
   default branch (`git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null`, or
   `origin/main` / `origin/master`, or local `main` / `master`).
2. Compute merge-base: `MB=$(git merge-base HEAD <base>)`.
3. Gather the patch: `git diff "$MB"` — diff from merge-base to the current working tree
   (includes committed branch commits and local index/worktree changes).
4. Surface untracked files: `git status --porcelain` (same as other targets — diff never
   shows untracked content).
5. Record in the report: target `branch changes`, base ref, merge-base sha, and the
   resolved command `git diff $(git merge-base HEAD <base>)`.

Phrases like "review my branch," "before I push," "pre-push review," or "review against
main" map here when the user means their full branch delta — not only staged hunks or a
single commit.

**Range of commits** (#6) is for explicit ref ranges beyond the branch-changes default:

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

Once the target is resolved: gather context per **Review Principles** (commit/PR
metadata, project norms), inspect the patch, then read surrounding code as needed —
impacted call sites and dependents, tests added/changed/missing, and whether the change
matches any intent implied by the current chat session.

**Resolution rule**: if the source is unspecified and cannot be inferred from context,
default to **staged changes** (`git diff --staged`) and proceed — state the assumed
target in the **Review Target** section of the output. Do not interrupt to ask unless
**Interactive Mode** is triggered.

When the user names a target explicitly, or context makes one clear (e.g. "review my
branch against main" or "before I push" → branch changes; "look at the last commit" →
HEAD; explicit `A..B` / `A...B` → commit range), use that instead of the default.

For **Interactive Mode** only, present this menu if the user hasn't already named a
target:

```
1. Staged changes
2. Unstaged changes
3. All changes (staged + unstaged working tree)
4. Last commit (HEAD)
5. Specific commit
6. Range of commits
7. Branch changes (pre-push vs default/base branch)
```

- If they pick 5: ask for the commit SHA or ref.
- If they pick 6: ask "What's the range? Give me a base and tip (e.g. `main..my-branch`
  or `main...my-branch`), or tell me how many recent commits (e.g. 'last 5 commits')."
- If they pick 7: ask for the base ref only when it isn't obvious (default: repo default
  branch).

## Empty Or Blocked Diff

After gathering the patch, handle these cases before running scope passes:

**Empty diff** — no changed hunks and no relevant untracked files:

- Stop the review workflow; do not produce a full report.
- Tell the user in one sentence that there was nothing to review (state the resolved
  target and command).
- Optionally note if untracked files were listed but the user did not ask to include them.

**Blocked diff** — git commands fail (not a repo, unknown ref, merge-base missing, dirty
state blocking checkout, etc.) or the patch is unusably empty while `git status` shows
changes:

1. State the blocker briefly.
2. Fall back to **natural-language review**: build a change list from `git status
   --porcelain`, `git diff --name-only`, recent `git log`, or paths the user named in
   chat. Read those files directly.
3. Write a `Change description` block — one header per file
   (`<path> (added|modified|deleted|renamed)`) with bullets of what changed; mention
   line ranges when known.
4. Proceed with the review against that description; mark the report target as
   `natural-language fallback` and list which files were read instead of a unified diff.
5. Do not silently pretend a git diff succeeded.

**Untracked-only changes** — status shows new files but no diff hunks:

- Read the untracked files (or ask once whether to include them if the set is large).
- Note in **Review target** that coverage is untracked-file review, not a git patch.

## Large-Diff Handling

Measure patch size after gathering (approximate changed lines from diff output, plus
changed file count from `git diff --name-only` / status). When the change is large, adapt
before scope passes — do not skim the entire patch in one pass.

**Thresholds** (either triggers large-diff mode):

- **> ~500 changed lines** in the unified diff, or
- **> ~20 changed files**

**Strategy**:

1. **Triage files by risk** — review highest-risk paths first: auth/authz, security
   boundaries, concurrency, migrations/schema, public API surface, dependency manifests,
   config defaults, error handling on new code paths. Defer generated code, lockfiles-only
   churn, and pure formatting unless a selected scope requires them.
2. **Chunk the work** — at `standard`/`deep`, review file-by-file or by logical
   directory; at `basic`, triage then skim only the top-risk files within the finding cap.
3. **Read surrounding code per chunk** — call sites and tests for each chunk before moving
   on; do not load the whole repo.
4. **Record coverage gaps** — in the report **Review target** section, list files or
   areas reviewed vs deferred; if large-diff mode forced truncation, say so explicitly
   under **Effort used**.
5. **Finding caps still apply** — large diffs do not raise caps; prioritize severity over
   breadth.

If the user asked for `deep` on a very large diff, run parallel scope passes **per chunk**
or per high-risk file group rather than pasting the entire diff into each subagent prompt.

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
   commit / commit range / branch changes)
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
3. **Gather context and the diff** — read `<SKILL_ROOT>/references/review-principles.md`
   (**Context to gather first**); run the resolved git command(s); apply **Empty Or
   Blocked Diff** rules if the patch is empty or git fails; apply **Large-Diff Handling**
   when thresholds are met; run focused automated checks when feasible and record
   results; read surrounding code, call sites, and existing tests as needed.
4. **Run the review**, branching by effort:
   - `basic`: one combined pass across selected scopes, no verify.
   - `standard`: Scope & Intent Alignment, then one pass per selected scope, then a
     lightweight verify.
   - `deep`: Scope & Intent Alignment (inline, by you — see next section for why), then
     parallel per-scope passes (or sequential if your tool has no parallel agents), then
     dedup, then adversarial verify, then a gap-sweep pass.
5. **Validate findings** (standard/deep) — apply the **Finding quality bar** from
   `review-principles.md`: verify each against the diff and surrounding code, prefer
   concrete evidence over speculation, distinguish confirmed issues from open questions,
   and dedupe across scopes.
6. **Assemble and return the report** using
   `<SKILL_ROOT>/references/review-report-template.md` (see **Output Contract**).

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

Return a code review report in chat after the review finishes. **Use
`<SKILL_ROOT>/references/review-report-template.md` as the single source of truth** for
section order, field names, severity labels, and formatting — unless the user requested
a different format. Findings-first; keep process narration brief.

When git diff was empty, follow **Empty Or Blocked Diff** instead of emitting a full
template. When large-diff mode truncated coverage, fill in the template's coverage fields.

Do not duplicate the template body here — read it before assembling the report.

## Routing Findings Back

Findings that need code changes route back into the lifecycle by type. State the recommended
route in the report so the fix does not stall:

- Missing or incorrect behavior → implementation via [../plan-executor/SKILL.md](../plan-executor/SKILL.md) or a direct scoped edit.
- Regression, crash, or unexplained failure → [../debugging-guide/SKILL.md](../debugging-guide/SKILL.md) to prove root cause before changing code.
- Design or architecture mismatch → [../plan-guide/SKILL.md](../plan-guide/SKILL.md) to plan the repair.
- Missing or weak tests → [../test-driven-dev-guide/SKILL.md](../test-driven-dev-guide/SKILL.md), or [../implementation-auditor/SKILL.md](../implementation-auditor/SKILL.md) for requirement-level proof.

After the author applies fixes, re-run this skill on the amended diff before delivery. This
skill does not apply the fixes itself.

## Posting to GitHub

This skill produces the **review content** — findings, severity, and merge verdict — as an
in-chat report. It does not call `gh` or post to GitHub itself.

When the user asks to **post the review on GitHub** (or "submit review comments on the PR",
"REQUEST_CHANGES on GitHub", etc.) and the repo remote is GitHub:

1. Finish this skill's review workflow and return the full report per
   `review-report-template.md` first — unless findings from a prior run in the same
   session are already complete.
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

- Apply **Finding quality bar** and **Constructive feedback** from
  `review-principles.md` to every finding.
- Findings must be the primary content of the response.
- Keep summaries brief compared with the findings section.
- Prefer concrete, actionable fixes over vague advice.
- Reference exact files and lines when practical.
- Call out missing tests explicitly when change risk warrants it.
- Do not report style or formatting nits unless they violate documented project norms or
  hide a real defect.
- If no findings are discovered, say that explicitly and mention any residual risks or
  testing gaps.
- Note substantive strengths in **What went well** when present — briefly, without filler
  praise.
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

`<SKILL_ROOT>/references/review-principles.md` — mandatory reviewer mindset, context
gathering, finding quality bar, constructive feedback, and PR hygiene.

`<SKILL_ROOT>/references/review-report-template.md` — default structure for the final
in-chat report.

`<SKILL_ROOT>/references/scope-checklists.md` has the full bullet list per scope — read it
before running any scope's pass, and required verbatim in parallel pass prompts at `deep`
effort.
