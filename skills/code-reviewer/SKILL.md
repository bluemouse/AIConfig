---
name: code-reviewer
description: "Review git diffs and commits (staged, unstaged, working tree, commit, range, or branch) across six lenses and three effort tiers, returning a structured findings-first report with proposed fixes. Use for code, diff, branch, security, performance, design, or test review of changes — including interactive mode ('review interactively') — even when phrased as 'check this commit/diff for regressions or issues before I push/merge'. Does not trigger on active local merge/rebase integration (git-merge-guide) or codebase learning guides (code-professor)."
---

# Code Reviewer

Resolve `<SKILL_ROOT>` as the directory containing **this** skill's `SKILL.md`, and resolve `references/` paths from it.

Multi-scope code review driven by three axes that default silently unless **Interactive Mode** is triggered: **source** (staged changes), **scope** (all six lenses), and **effort** (`standard`).

## Primary Directive and Boundaries

Review code changes; do not implement fixes unless explicitly asked in a follow-up. Mandatory foundation for every review: `<SKILL_ROOT>/references/review-principles.md` (mindset, context gathering, documentation-impact checkpoint, finding quality bar, and constructive feedback). Route broad documentation audits to [techdoc-reviewer](../techdoc-reviewer/SKILL.md).

**When NOT to use:** during active local merge/rebase integration, stay in [../git-merge-guide/SKILL.md](../git-merge-guide/SKILL.md); when no change set exists (onboarding, architecture guides), use [../code-professor/SKILL.md](../code-professor/SKILL.md).

## Resolving Source, Scope, and Effort

- **Source** (record the resolved target in **Review target**): **staged** (`git --no-pager diff --staged`, default), **unstaged** (`git --no-pager diff`), **working tree** (`git --no-pager diff HEAD`), **last commit** (`git --no-pager show HEAD`), **specific commit** (`git --no-pager show <sha>`), **commit range** (prefer three-dot `A...B` merge-base diff over `A..B`; ask one line only if genuinely ambiguous), or **branch changes** (`git --no-pager diff $(git merge-base HEAD <base>)`).
  - Always run git in sync mode with `--no-pager`, and pair `git diff` with `git status --porcelain` so untracked files are inspected.
  - **Empty diff** (no hunks or relevant untracked files): stop and state what target was checked in one sentence — do not emit the template. **Blocked diff**: state the git blocker, inspect changed/named files directly, and mark target `natural-language fallback`. **Untracked-only**: review untracked files (ask once if large) and note untracked coverage.
  - **Large diffs (> ~500 lines or > ~20 files):** triage high-risk areas first (auth/security boundaries, concurrency, migrations, public APIs, dependency/config changes; defer generated/lockfile/formatting churn), review in chunks with local context, record reviewed vs deferred files in the report, and keep finding caps unchanged (at `deep`, run parallel passes per chunk/risk group).
- **Scope:** `design`, `correctness`, `maintainability`, `security`, `performance`, `tests` (default: all six). Read `<SKILL_ROOT>/references/scope-checklists.md` (plus matching **Conditional Extensions**) right before each pass. **Scope & Intent Alignment** always runs first as shared context.
- **Effort:**
  - **`basic`** (cap **5**): single combined read across selected scopes, no verification pass; for small/low-risk diffs or "quick look" requests.
  - **`standard`** (default, cap **10**): Scope & Intent Alignment → sequential pass per selected scope → lightweight diff/context verification and cross-scope dedup.
  - **`deep`** (cap **15–20**): Scope & Intent Alignment inline → one independent pass per selected scope (concurrent subagents when supported, else sequential with separate notes; paste scope bullets verbatim from `scope-checklists.md`) → cross-scope dedup → recall-biased adversarial verify (`CONFIRMED` / `PLAUSIBLE` / `REFUTED`) → fresh gap-sweep read. Full prompt template, verification rules, and per-host dispatch mechanics live in [references/parallel-scope-passes.md](references/parallel-scope-passes.md).
- **Interactive Mode** ("review interactively", "ask me first", "guided review", "walk me through it"): ask about all three axes (target + ref if needed, scopes, effort) in one message before starting.

## Review Workflow and Output Contract

1. Resolve source, scope, and effort (or run the Interactive Mode prompt).
2. Gather diff, untracked files, surrounding call sites/tests, and feasible focused test/lint checks per `references/review-principles.md`.
3. Run the bounded documentation-impact checkpoint (`review-principles.md`) and execute the selected effort workflow (`basic` / `standard` / `deep`).
4. Return a findings-first report following `<SKILL_ROOT>/references/review-report-template.md` (the single source of truth for sections, finding fields, severities, `root-cause-phase`, and verdict labels). State explicitly when no findings were discovered alongside residual risks or test gaps.
   - **Artifact path:** in chat by default; `.agents/plans/<feature-or-topic-slug>-code-review.md` when the user asks to save standalone; or the orchestrator-assigned path (e.g. `.agents/workflow/<slug>/40-code-review.md`) inside `dev-workflow-orchestrator`.

## Routing Findings, Re-review, and GitHub Delivery

- **Routing findings back:**
  - `root-cause-phase: local` (discrete diff defects) → [../code-review-resolver/SKILL.md](../code-review-resolver/SKILL.md)
  - Multi-task implementation gaps → [../plan-executor/SKILL.md](../plan-executor/SKILL.md)
  - Unexplained regression or crash → [../debugging-guide/SKILL.md](../debugging-guide/SKILL.md)
  - Design/architecture mismatch → [../plan-guide/SKILL.md](../plan-guide/SKILL.md)
  - Missing/weak tests or requirement proof → [../test-driven-dev-guide/SKILL.md](../test-driven-dev-guide/SKILL.md) or [../implementation-auditor/SKILL.md](../implementation-auditor/SKILL.md)
  - Broad doc drift → [../techdoc-reviewer/SKILL.md](../techdoc-reviewer/SKILL.md); PR sizing/split → [../github-guide/SKILL.md](../github-guide/SKILL.md); git mechanics → [../git-guide/SKILL.md](../git-guide/SKILL.md)
- **Re-review mode** (after `code-review-resolver`): verify each `fixed` finding on the amended diff (open a new finding referencing the original id if incomplete), carry forward `unresolved`/`deferred` findings, run a fresh pass for regressions introduced by fixes, and continue until the loop verdict is `ready to commit` or `ready with notes` (or round cap 5 is hit).
- **Posting to GitHub:** always return the in-chat report first (unless explicitly asked to post silently), then hand off `gh` review posting (`gh auth status`, `gh pr view`, inline comments, verdict mapping) to [../github-guide/SKILL.md](../github-guide/SKILL.md).

## Resources

- `<SKILL_ROOT>/references/review-principles.md` — mandatory mindset, context gathering, doc-impact checkpoint, and finding quality bar
- `<SKILL_ROOT>/references/review-report-template.md` — canonical report schema and verdict rules
- `<SKILL_ROOT>/references/scope-checklists.md` — per-scope checklists, conditional extensions, and Scope & Intent Alignment
- `<SKILL_ROOT>/references/parallel-scope-passes.md` — `deep`-effort prompt template, reconciliation/verify/gap-sweep rules, and per-host dispatch mechanics
