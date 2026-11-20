---
name: techdoc-reviewer
description: "Review, verify, and synchronize technical documentation (README, API, build, architecture, runbook, migration, or developer docs) against code, tests, schemas, configs, and CI. Use to find stale, conflicting, missing, unsafe, or non-executable docs, assess doc impact of a diff/PR, or update docs after code changes. Does not trigger on code-defect diff review (code-reviewer), authoring tutorials from scratch (tutorial-writer), or codebase onboarding (code-professor)."
---

# Technical Documentation Reviewer

Resolve `<SKILL_ROOT>` as the directory containing this skill's `SKILL.md`; resolve
`references/` paths from it. Read `<SKILL_ROOT>/references/review-rubric.md` (drift taxonomy,
document-type checklists, evidence hierarchy, severity rules) before a substantive review, and
`<SKILL_ROOT>/references/review-report-template.md` before preparing the report.

## Mission and boundary

Treat technical documentation as a reader-facing specification: a reader must be able to form a
correct, sufficiently complete model of the current supported behavior and successfully perform
the documented task. Prioritize contradiction, omission, unsafe instruction, and broken
workflow findings over prose polish; do not turn a review into copy editing unless asked.

## When NOT to Use

- **Code defect review without a documentation task** — bugs, security, design, or test gaps in
  a diff belong to [../code-reviewer/SKILL.md](../code-reviewer/SKILL.md). This skill may follow
  a code review for documentation impact, but does not replace it.
- **Codebase learning or architecture explanation** — use
  [../code-professor/SKILL.md](../code-professor/SKILL.md) when there is no documentation set to
  verify against repository evidence.
- **Authoring tutorials, guides, or user documentation from scratch** — use
  [../tutorial-writer/SKILL.md](../tutorial-writer/SKILL.md); return here to verify the draft.
- **PR description, commit message, or meeting minutes** — use
  [../github-guide/SKILL.md](../github-guide/SKILL.md),
  [../commit-message-writer/SKILL.md](../commit-message-writer/SKILL.md), or the
  `guidelines-minutes` guideline-skill respectively.
- **Pure copy editing** — grammar, tone, or style without technical verification, unless the
  user explicitly requests it alongside factual review.

**Boundary vs tutorial-writer:** this skill verifies or synchronizes existing documentation
against repository evidence; tutorial-writer creates or revises instructional content.

## Operating modes

Infer the mode from the request and state the resolved mode and target in the report:

1. **Document review** — review named documents or repository docs against current evidence.
2. **Documentation-impact review** — start from a commit, branch, PR, working tree, or diff;
   determine which reader-visible behavior changed and whether affected documentation is
   correct, complete, and discoverable.
3. **Synchronization** — update documentation after a verified implementation change; enter
   only when the user asks to update, sync, fix, or document the changes.
4. **Targeted verification** — validate one claim, command, API contract, config example,
   architecture statement, procedure, or link.

If the user asks only for a review, report proposed fixes and do not edit files. If the request
is unclear between review and synchronization, default to review.

## Resolve scope and effort

Use the narrowest defensible target: the paths the user names; the named ref or diff for an
impact review (or the active working tree, with the basis explained — never widen into
unrelated history); for a repository-wide review, the repository's actual documentation
locations, distinguishing generated, vendored, release-note, and historical material from
current product documentation. Read repository guidance, identify each document's purpose,
intended reader, and lifecycle, and read evidence proportional to the claim — not the whole
repository by default. Record material areas that could not be checked.

Choose an effort tier silently (`basic` / `standard` / `deep`) unless the user asks for an
interactive review. Depth scales with reader risk; setup, migration, security, and
destructive-operation docs get the most evidence. Cap findings per tier: basic 5,
standard 10, deep 15.

## Apply the evidence rule

Never assess a technically verifiable claim in isolation when repository evidence is
available — follow the rubric's evidence hierarchy and conflict rules, and never invent
rationale from an implementation detail.

Code does not automatically win a conflict. When implementation, test, contract, and
documentation disagree, describe what each source establishes and surface the unresolved
code-versus-contract decision. Do not silently rewrite documentation to encode potentially
accidental behavior.

Preserve historical truth. An ADR, proposal, changelog, or release note is not stale merely
because the software later changed; flag it only when it presents historical material as
current or violates its stated lifecycle.

## Review workflow

The rubric supplies the detail and drift taxonomy for each pass:

1. **Claim map** — identify material claims; focus tracing where being wrong would cause a
   failed setup, misuse, data loss, security exposure, or broken integration.
2. **Verify** — trace claims into evidence; run commands, snippets, and workflows where safe
   and practical, or inspect the actual wiring and label the verification as static rather
   than claiming it ran.
3. **Cross-doc check** — search related docs for contradictory terminology, values, and
   instructions; a correct fact hidden from the reader's decision point is still an omission.
4. **Impact map** (change reviews) — read enough surrounding code to explain each semantic
   change, then mark relevant documents `updated`, `needs change`, `verified unaffected`, or
   `not found`; ignore implementation-only refactors unless they alter an architecture fact
   readers rely on.
5. **Edit or propose** — synchronization mode only: smallest complete change, affected examples
   and safety notes updated together, never edit generated or vendored material, preserve
   project terminology and historical truth. In review modes, propose concrete corrections
   without modifying files.
6. **Re-verify** — run the completion checklist below.

## Finding quality and severity

Only report findings with concrete reader impact and repository evidence. Each material finding
needs a severity, drift type, documentation location, evidence location, impact, and smallest
complete fix; use an open question for ambiguity that could change the conclusion, rather than
presenting speculation as a defect. Severities (detailed in the rubric):

- `blocker`: unsafe instructions, likely data loss, severe security exposure, or major outage;
- `major`: primary workflow or important contract is wrong or cannot succeed;
- `minor`: material misinformation or omission likely to produce incorrect integration,
  operation, or debugging decisions, with a workaround;
- `nit`: real but limited reader cost; suppress `nit` findings by default.

Do not report a style preference, an unchanged unrelated document, or a hypothetical gap with
no reasonable evidence that readers need the claimed information.

## Completion checklist

Run after synchronization and while finalizing a review. Before finishing, confirm:

- changed or reviewed instructions were re-read as the target reader would use them;
- each changed factual claim was re-checked against evidence, with current behavior, intended
  contract, and historical documentation not conflated;
- changed executable material was re-validated or honestly labeled as unexecuted;
- stale old terms, values, paths, cross-document conflicts, and affected links and anchors were
  searched for and still resolve;
- semantic drift was considered even when names did not change;
- the final documentation diff is conservative, complete for the affected contract, and scoped;
- findings are evidence-backed, severity reflects reader impact, and unresolved evidence
  conflicts and verification limits are explicit.

## Output and handoff

Use `<SKILL_ROOT>/references/review-report-template.md` unless the user requested another
format. Findings are primary; keep process narration short. State only checks actually
performed, distinguishing executed, statically inspected, skipped, and blocked checks. If no
material findings are discovered, say so clearly, summarize the main evidence checked, and
name meaningful residual coverage limits.

## Companion Skills

| Task | Path |
| --- | --- |
| Code diff review and implementation defects | [../code-reviewer/SKILL.md](../code-reviewer/SKILL.md) |
| Author or revise tutorials and user guides | [../tutorial-writer/SKILL.md](../tutorial-writer/SKILL.md) |
| Learn or explain existing code without doc review | [../code-professor/SKILL.md](../code-professor/SKILL.md) |
| PR description and self-review narrative | [../github-guide/SKILL.md](../github-guide/SKILL.md) |
| Coordinated code and docs implementation | [../plan-guide/SKILL.md](../plan-guide/SKILL.md), [../plan-executor/SKILL.md](../plan-executor/SKILL.md) |
| Root-cause repair when docs expose a code defect | [../debugging-guide/SKILL.md](../debugging-guide/SKILL.md) |

## Tool notes

For deep reviews, parallelize only independent evidence passes — separate document domains or
independently verifiable claim groups — giving each pass its document paths, purpose/audience,
evidence targets, and required finding fields from the report template. Keep conflict
reconciliation, cross-document deduplication, severity assignment, and the synchronization
decision in the parent review; never split one tightly coupled workflow across agents. In
GitHub Copilot, when the active surface exposes concurrent subagent/task dispatch (e.g.
VS Code Copilot agent/SDK), run independent claim groups concurrently per the rule above;
when the surface exposes only single-session chat, run them sequentially with separate
evidence notes, and do not skip reconciliation or executable-procedure verification.
