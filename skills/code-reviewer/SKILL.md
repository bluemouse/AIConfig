---
name: code-reviewer
description: Review git diffs and commits — staged, unstaged, branch, working tree, commit, or range — and return a structured, findings-first report with proposed fixes. Use when reviewing code, diffs, branch changes, or pre-push commits, or for security/performance/design/test review of recent changes — even without saying "code review" (e.g. "check this diff", "review my branch against main"). Supports six scopes, three effort levels, and interactive mode ("review interactively"). Does not trigger on active local merge/rebase integration review (git-merge-guide) or codebase learning guides (code-professor).
---

# Code Reviewer

Resolve `<SKILL_ROOT>` as the directory containing **this** skill's `SKILL.md`. Resolve
paths to `references/`, `scripts/`, and `assets/` from that directory.

A multi-scope code review workflow driven by three axes with safe defaults — don't ask
about any axis unless the user explicitly wants a guided setup (see **Interactive
Mode**): **source** (what to diff; defaults to staged changes), **scope** (which lenses;
defaults to all six), **effort** (how deep; defaults to `standard`).

## Primary Directive

Review code changes; do not implement them. Follow
`<SKILL_ROOT>/references/review-principles.md` for reviewer mindset, context gathering,
finding quality, constructive feedback, and PR hygiene — it is mandatory for every
review, not optional depth reading. Include its bounded documentation-impact checkpoint
for reader-visible semantic changes; hand off broad documentation audits to
[techdoc-reviewer](../techdoc-reviewer/SKILL.md).

**When NOT to use this skill**: during active local merge/rebase integration review,
stay in [../git-merge-guide/SKILL.md](../git-merge-guide/SKILL.md) (this skill comes
afterward for an optional read-only final diff review); with no change set to review
(codebase learning, onboarding, architecture guides), use
[../code-professor/SKILL.md](../code-professor/SKILL.md).

## Resolving The Source (Review Target)

Resolve one of: **staged** (`git --no-pager diff --staged`, the default when unspecified
and uninferable), **unstaged** (`git --no-pager diff`), **all working tree**
(`git --no-pager diff HEAD`), **last commit** (`git --no-pager show HEAD`), **specific
commit** (`git --no-pager show <sha-or-ref>`), **commit range**, or **branch changes**
(pre-push). State the assumed target in the **Review Target** section; do not ask
unless **Interactive Mode** is triggered.

Durable git gotchas for every target:

- Run all git commands in sync terminal mode with `--no-pager` (or `GIT_PAGER=cat`) —
  `git diff`/`show`/`log` block on the pager when stdout is a TTY.
- `git diff` never shows untracked content: run `git status --porcelain` alongside and
  read any untracked files.
- **Branch changes**: resolve the base (user-named, else the repo default branch),
  compute the merge-base, and diff from it — `git --no-pager diff $(git merge-base HEAD
  <base>)` — so post-divergence base commits don't pollute the patch; it also includes
  local uncommitted edits. **Range**: prefer three-dot `A...B` (merge-base diff, the
  usual "my branch vs main") over two-dot `A..B` (literal tree-to-tree); if genuinely
  unclear which is meant, ask one line.

**Empty diff** (no hunks, no relevant untracked files): stop — tell the user in one
sentence what target was checked; no report. **Blocked diff** (git fails or the patch
is unusable): state the blocker, then fall back to **natural-language review** — build
a change list from `git status --porcelain`, `git --no-pager diff --name-only`, recent
log, or user-named paths, read those files, review against a per-file `Change
description` block, and mark the report target `natural-language fallback`; never
pretend a diff succeeded. **Untracked-only changes**: read the untracked files (ask
once whether to include them if the set is large) and note in **Review target** that
coverage is untracked-file review, not a git patch.

## Large-Diff Handling

Triggers on **> ~500 changed lines** or **> ~20 changed files** (either). Do not skim the
entire patch in one pass: triage by risk (auth/authz, security boundaries, concurrency,
migrations/schema, public API surface, dependency manifests, config defaults, new error
paths first; defer generated code, lockfile-only churn, pure formatting); chunk file-by-file
or by logical directory (`basic`: triage then skim only top-risk files within the cap),
reading surrounding code per chunk rather than the whole repo; record reviewed vs
deferred files under **Review target** and any truncation under **Effort used**. Finding
caps still apply — large diffs do not raise them; prioritize severity over breadth. At
`deep` on a very large diff, run parallel scope passes **per chunk** or high-risk file
group, not one whole-diff prompt per subagent.

## Selecting Scope

Six selectable lenses: `design`, `correctness`, `maintainability`, `security`,
`performance`, `tests`. Full checklists — each opening with a *how to look* heuristic —
live in `<SKILL_ROOT>/references/scope-checklists.md`; read the relevant section right
before running that scope's pass (at `deep`, paste its bullets verbatim into that scope's
parallel pass prompt), and fold in any matching **Conditional Extensions** checks (new
HTTP routes, migrations, dependency bumps, UI changes, etc.). **Scope & Intent Alignment
always runs** — it's foundational context-gathering, not a domain lens, so it's not a
selectable option; its checklist is at the bottom of the same file. **Default**: unnamed
scope → run all six; do not prompt just because scope alone is unspecified.

## Selecting Effort

**`basic`** — one combined pass across selected scopes in a single read of the diff, no
verification; report what's directly evident. Cap at **5** findings. Use when the user
asks for "quick" / "basic" / "just a quick look," or the diff is small and low-risk.

**`standard`** (default) — Scope & Intent Alignment first, then one sequential pass per
selected scope (notes per scope), then a lightweight verify: reread the diff per
candidate, drop unevidenced findings, dedupe across scopes. Cap at **10** findings.

**`deep`** — full rigor via parallel scope passes when the environment supports them
(see **Deep Effort: Parallel Scope Passes** and `## Tool notes`): per-scope passes →
cross-scope dedup → adversarial verify → final gap sweep. Cap at **15–20** findings.

## Interactive Mode

Trigger phrases: "review interactively," "ask me first," "guided review," "walk me
through it," or equivalent. When triggered, ask about all three axes together in one
message — even overriding anything already stated, to confirm — before starting: (1)
the review target (staged / unstaged / all changes / last commit / specific commit /
commit range / branch changes), (2) the scopes (default: all six), and (3) the effort
(default: standard). Ask for the SHA/ref, range endpoints, or base ref only when not
already supplied. Outside interactive mode, all three axes default silently per the
rules above.

## Review Workflow

1. **Resolve source** — per the rules above; default to staged changes if it can't be
   determined.
2. **Resolve scope & effort** — defaults, or the interactive menu if triggered.
3. **Gather context and the diff** — per `review-principles.md` (**Context to gather
   first**): run the resolved git command(s); apply **empty-or-blocked-diff rules** and
   **Large-Diff Handling** as triggered; run focused automated checks when feasible and
   record results; read surrounding code, call sites, and existing tests as needed. Chat
   context (requirements, decisions, known bugs, risk tolerance discussed earlier)
   sharpens the review but never replaces direct inspection of the diff.
4. **Run the documentation-impact checkpoint** — per `review-principles.md`: one bounded
   finding for undocumented or contradicted reader-visible semantic changes; route broad
   documentation work to [techdoc-reviewer](../techdoc-reviewer/SKILL.md).
5. **Run the review** by effort: `basic` — one combined pass, no verify; `standard` —
   alignment, per-scope passes, lightweight verify; `deep` — alignment inline, parallel
   per-scope passes (sequential if no parallel agents), dedup, adversarial verify,
   gap-sweep.
6. **Validate findings** (standard/deep) — apply the **Finding quality bar** from
   `review-principles.md`: verify against the diff and surrounding code, prefer concrete
   evidence over speculation, dedupe across scopes.
7. **Assemble and return the report** using
   `<SKILL_ROOT>/references/review-report-template.md` (see **Output Contract**).

## Deep Effort: Parallel Scope Passes

`deep` effort only. Run Scope & Intent Alignment yourself first — shared intent context
every scope pass needs, computed once so passes don't guess independently. Then dispatch
**one independent pass per *selected* scope**, in a single turn when the environment
supports parallel subagents (otherwise sequentially, notes separate per scope). Each
pass receives the full resolved diff (or exact commands to reproduce it), a 2–5 sentence
intent summary from your alignment pass, and that scope's checklist bullets pasted
verbatim from `references/scope-checklists.md` — parallel passes do not have this
SKILL.md loaded, so paste real content, not pointers — and returns up to 6 candidates
(Severity, Location, What's wrong, Why it matters, Proposed fix). Then, yourself:
**dedupe** across scopes (merge same-issue findings at the higher severity);
**adversarially verify** each candidate against the exact hunk and surrounding code —
CONFIRMED / PLAUSIBLE / REFUTED, recall-biased (default PLAUSIBLE when unsure), drop
REFUTED; **gap-sweep** with one fresh read for defect classes nothing caught (e.g. a
dropped guard clause, a shrunken lock scope, a flipped config default, an unaddressed
checklist bullet). Cap the final list at **15–20** findings. Prompt template, alignment
rationale, and per-environment dispatch:
`<SKILL_ROOT>/references/parallel-scope-passes.md`.

## Output Contract

Return a findings-first report in chat using
`<SKILL_ROOT>/references/review-report-template.md` as the **single source of truth**
for section order, field names, severity labels, and formatting — unless the user
requested a different format; keep process narration brief and do not duplicate the
template body here. When git diff was empty, follow **empty-or-blocked-diff rules** instead of
emitting a full template; when large-diff mode truncated coverage, fill in the
template's coverage fields. Apply the **Finding quality bar** and **Constructive
feedback** sections of `review-principles.md` to every finding; state explicitly when no
findings were discovered (mentioning residual risks or testing gaps). Do not rewrite or
patch the code unless the user explicitly asks in a follow-up — this skill only
proposes fixes.

### Artifact output path

Outside the dev-workflow-orchestrator, when the user wants the report saved as a file,
write it to `.agents/plans/<feature-or-topic-slug>-code-review.md` (gitignored; never to
the repository root). Inside the orchestrator, use the orchestrator-assigned path
(typically `.agents/workflow/<slug>/40-code-review.md`). When the user has not asked for
a file, return the report in chat without writing a file.

## Routing Findings Back

Findings that need code changes route back into the lifecycle by type; state the
recommended route in the report so the fix does not stall:

- `root-cause-phase: local` (discrete code defects in the current diff) → [../code-review-resolver/SKILL.md](../code-review-resolver/SKILL.md) for targeted fixes and a fix report for re-review.
- Behavior spanning multiple tasks → implementation via [../plan-executor/SKILL.md](../plan-executor/SKILL.md).
- Regression, crash, or unexplained failure → [../debugging-guide/SKILL.md](../debugging-guide/SKILL.md) to prove root cause before changing code.
- Design or architecture mismatch → [../plan-guide/SKILL.md](../plan-guide/SKILL.md) to plan the repair.
- Missing or weak tests → [../test-driven-dev-guide/SKILL.md](../test-driven-dev-guide/SKILL.md), or [../implementation-auditor/SKILL.md](../implementation-auditor/SKILL.md) for requirement-level proof.
- Documentation missing, stale, unsafe, or contradictory → [../techdoc-reviewer/SKILL.md](../techdoc-reviewer/SKILL.md).
- Diff too large or mixed concerns → [../github-guide/SKILL.md](../github-guide/SKILL.md) for split/self-review; commit, push, rebase, worktree mechanics → [../git-guide/SKILL.md](../git-guide/SKILL.md).

After fixes are applied (via code-review-resolver for `local` findings), re-run this
skill on the amended diff before delivery. This skill does not apply the fixes itself.

## Re-review mode

When invoked as a re-review after [../code-review-resolver/SKILL.md](../code-review-resolver/SKILL.md),
the input includes a finding disposition (which finding ids were `fixed`, `unresolved`,
`deferred`, or `upstream`) and the amended diff. In re-review mode:

1. **Verify fixed findings** — for each finding id marked `fixed`, confirm the amended
   diff actually resolves the issue; if the fix is incomplete or wrong, raise a new
   finding referencing the original finding id.
2. **Carry forward unresolved/deferred findings** — mark them still-open in the
   re-review report.
3. **Fresh pass for new findings** — run the standard review workflow on the amended
   diff to catch issues introduced by the fixes.
4. **Loop continuation** — the loop continues until the verdict is `ready to commit` or
   `ready with notes`, or the round cap (5) is hit.

## Posting to GitHub

This skill produces the review content as an in-chat report; it does not call `gh` or
post to GitHub itself. Finish the review and return the full report first, then hand off
delivery (severity-to-verdict mapping, inline comments, `REQUEST_CHANGES`/`COMMENT`
event) to **[github-guide](../github-guide/SKILL.md)** per its **Handoff from
code-reviewer** section. Confirm auth and PR number (`gh auth status`, `gh pr view`)
before posting. On non-GitHub hosts, say the handoff applies only to GitHub. For a
combined "review this PR and post on GitHub" request, run both skills in that order — do
not skip the in-chat report unless the user explicitly asks to post silently.

## Resources

- `<SKILL_ROOT>/references/review-principles.md` — mandatory reviewer mindset, context
  gathering, finding quality bar, constructive feedback, and PR hygiene.
- `<SKILL_ROOT>/references/review-report-template.md` — default structure for the final
  in-chat report.
- `<SKILL_ROOT>/references/scope-checklists.md` — full bullet list per scope; read it
  before running any scope's pass, and required verbatim in parallel pass prompts at
  `deep` effort.
- `<SKILL_ROOT>/references/parallel-scope-passes.md` — deep-effort dispatch: scope-pass
  prompt template, reconciliation/verify/gap-sweep detail, and **per-environment
  dispatch mechanics, including the per-tool deltas (Claude Code, Claude.ai, Cursor,
  GitHub Copilot)**.
