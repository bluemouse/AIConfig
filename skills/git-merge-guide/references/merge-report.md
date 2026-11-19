# Merge reporting

Use two reporting levels. Always produce a compact inline summary. Generate the detailed merge report only when the user explicitly asks for a merge report or detailed report.

## Contents

- [Compact default summary](#compact-default-summary)
- [Detailed report trigger](#detailed-report-trigger)
- [Detailed report structure](#detailed-report-structure)
- [Accuracy rules](#accuracy-rules)

## Compact default summary

Keep the default response concise but make integration-specific fixes visible. Use this shape and adapt wording to the operation:

```text
Merge/Rebase: <operation and source/target refs>
Git state: <COMPLETED | RESOLVED AND STAGED | still active>
Integration verification: <VERIFIED SUCCESS | NOT VERIFIED>

Conflicts:
- <logical conflict/file summary>
- <semantic rewrites, if any>

Integration review:
- <non-conflicted interaction issues found/fixed>
- <unresolved decisions, if any>

Additional integration fixes:
- <important fix 1>
- <important fix 2>

Verification:
- <affected tests/suites and pass/fail totals>
- <build/typecheck/static/lint/format/codegen checks>
- <blocked/skipped required tests, if any>

Final local state:
- <HEAD/merge state/staged post-rebase fixes>
- push performed: no
- <remaining user action>
```

Highlight changes made specifically because the two branches interacted, especially modifications outside Git conflict markers.

## Detailed report trigger

Generate the detailed report only on an explicit request such as:

- "generate the merge report";
- "give me a detailed merge report";
- "document this rebase/merge".

Provide Markdown inline by default. Create/save a report file only when the user asks for a file/artifact.

## Detailed report structure

When explicitly requested, produce all thirteen sections below — one block each, adapting depth to the operation:

1. **Executive summary** — operation, source, target/upstream, merge base, original and final HEAD, Git status, verification status, overall result; then 1-3 concise paragraphs on scope, complexity, semantic work, and verification outcome.
2. **Change-set overview** — each side independently: major commits, intended behavior changes, APIs/types/state/config modified, tests, architectural assumptions; use recorded pre-operation SHAs.
3. **Conflict resolution log** — one entry per logical conflict: files, each side's intent, interaction, resolution and why, code changed outside conflict markers, focused validation.
4. **Non-conflicted integration review** — one entry per reviewed interaction: area, change sets involved, risk category, finding, evidence, resolution, files, verification; state the review boundary and include reviewed-safe high-risk interactions; do not imply every unchanged line was reviewed.
5. **Additional integration fixes** — one entry per fix: symptom/risk, root cause, why it appears only when combined, implementation, changed files, regression test, verification result.
6. **User decisions** — one entry per ambiguity gate: decision, options, recommendation, user choice, resulting implementation; state explicitly when none were required.
7. **Testing impact analysis** — why the final test set was considered affected (direct, transitive, component, cross-component, concurrency, platform/config/flag variants, compatibility, full suite) with the dependency/test-discovery evidence used.
8. **Verification results** — per command: command, reason selected, relevant scope, result; then passed/failed/skipped/blocked totals.
9. **Static and structural validation** — applicable checks only: unmerged entries, conflict-marker scan, `git --no-pager diff --check`, build, type checking, static analysis, lint, formatting, codegen consistency.
10. **Final integrated-state review** — behavior preserved from each side, intentional adaptations, invariants/contracts checked, combined design assumptions confirmed.
11. **Residual risks and unverified areas** — anything local evidence/testing could not prove (unavailable tests/hardware/platforms, under-exercised timing/concurrency, remaining assumptions); state explicitly if none were identified.
12. **Final Git state** — branch, HEAD, remaining operation metadata, unmerged entries, staged/unstaged/untracked changes, final merge commit created (no unless stated), remote operations (none); for rebase include old-to-new commit correspondence or a `range-diff` summary when useful.
13. **Required user actions** — actual remaining actions only: final merge commit via [../../git-guide/SKILL.md](../../git-guide/SKILL.md) (optionally [../../commit-message-writer/SKILL.md](../../commit-message-writer/SKILL.md)), reviewing staged post-rebase fixes, outstanding semantic decisions, tests on unavailable platforms, optional [../../code-reviewer/SKILL.md](../../code-reviewer/SKILL.md) diff review or [../../implementation-auditor/SKILL.md](../../implementation-auditor/SKILL.md) audit; state that no action remains when true.

## Accuracy rules

- Use exact locally observed SHAs, refs, commands, and results where available.
- Separate observed facts from inferred intent.
- Do not claim tests ran when they did not.
- Do not hide failed/skipped/blocked required tests inside prose.
- Do not claim a merge commit exists when the no-commit workflow intentionally left the merge staged.
- Do not claim remote publication; this skill performs no remote operations.
