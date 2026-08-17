---
name: techdoc-reviewer
description: "Review, verify, and synchronize technical documentation for software projects. Use when asked to review README, API, build, architecture, design, runbook, tutorial, migration, troubleshooting, or developer documentation; verify documentation against code, tests, schemas, configuration, build files, examples, or CI; find stale, conflicting, missing, unsafe, or non-executable docs; assess documentation impact of a commit, branch, PR, or diff; or update docs after an implementation change. Prioritize evidence-backed semantic drift and reader-blocking omissions over grammar or style. Complements code-reviewer: use this skill for documentation truth and coverage, and code-reviewer for defects in the implementation diff."
---

# Technical Documentation Reviewer

Resolve `<SKILL_ROOT>` as the directory containing this skill's `SKILL.md`. Resolve paths
to `references/` from that directory.

## Mission and boundary

Treat technical documentation as a reader-facing specification of the software. Its central
quality invariant is that a reader can form a correct, sufficiently complete model of the
current supported behavior and successfully perform the documented task.

This skill reviews documentation and its relationship to repository evidence. It does not
replace a code review:

- Use **code-reviewer** to find defects, design risks, security issues, and missing tests in
  a change set.
- Use **techdoc-reviewer** to verify the truth, completeness, safety, and executability of
  the documentation for that change or repository.
- For a combined implementation-and-documentation review, first establish the code change's
  semantics with `code-reviewer`, then use this skill to trace its documentation impact.
  Do not have either review silently stand in for the other.

Prioritize contradiction, omission, unsafe instruction, and broken workflow findings over
prose polish. Do not turn a documentation review into copy editing unless the user explicitly
asks for it.

## When NOT to Use

- **Code defect review without a documentation task** — when the user wants bugs, security,
  design, or test gaps in a diff, use [../code-reviewer/SKILL.md](../code-reviewer/SKILL.md).
  This skill may follow a code review for documentation impact, but does not replace it.
- **Codebase learning or architecture explanation** — use
  [../code-professor/SKILL.md](../code-professor/SKILL.md) when there is no documentation set
  to verify against repository evidence.
- **Authoring new tutorials, guides, or user documentation from scratch** — use
  [../tutorial-writer/SKILL.md](../tutorial-writer/SKILL.md). Return here afterward to verify
  the draft against the repository.
- **PR description, commit message, or meeting minutes** — use
  [../pull-request-guide/SKILL.md](../pull-request-guide/SKILL.md),
  [../commit-message-writer/SKILL.md](../commit-message-writer/SKILL.md), or
  [../minutes-writer/SKILL.md](../minutes-writer/SKILL.md) respectively.
- **Pure copy editing** — grammar, tone, or style without technical verification unless the
  user explicitly requests copy editing alongside factual review.

**Boundary vs tutorial-writer:** techdoc-reviewer verifies or synchronizes existing technical
documentation against repository evidence; tutorial-writer creates or revises instructional
content.

Read `<SKILL_ROOT>/references/review-rubric.md` for the drift taxonomy, document-type
checklists, evidence hierarchy, and severity rules before conducting a substantive review.
Read `<SKILL_ROOT>/references/review-report-template.md` before preparing the final report.

## Operating modes

Infer the mode from the request. State the resolved mode and target in the report.

1. **Document review** — review named documents, a documentation area, or repository docs
   against current evidence.
2. **Documentation-impact review** — begin with a commit, branch, PR, working tree, or diff;
   determine which reader-visible behavior changed and whether affected documentation is
   correct, complete, and discoverable.
3. **Synchronization** — update documentation after a verified implementation change. Enter
   this mode only when the user asks to update, sync, fix, or document the changes.
4. **Targeted verification** — validate one claim, command, API contract, configuration
   example, architecture statement, procedure, or link.

If the user asks only for a review, report proposed fixes and do not edit files. If the request
is unclear between review and synchronization, default to review rather than changing docs.

## Resolve scope and effort

Use the narrowest defensible target:

- Review the paths the user names.
- For a documentation-impact review, use the named ref or diff. If none is named, inspect the
  active working tree and explain the chosen basis; do not widen into unrelated history.
- For a repository-wide docs review, identify the repository's actual documentation locations
  from project guidance and structure. Do not assume every Markdown file is current product
  documentation: distinguish generated, vendored, release-note, and historical material.

Choose an effort tier silently unless the user asks for an interactive review:

| Tier | Use | Required rigor |
| --- | --- | --- |
| `basic` | Quick check or small, low-risk docs | Trace only directly material claims; do not report more than five findings. |
| `standard` (default) | Ordinary documentation or change review | Inventory the document's important claims, validate them against relevant evidence, test executable material when practical, search for material cross-document conflicts, and re-check every candidate finding. Cap at ten findings. |
| `deep` | Public APIs, setup paths, migrations, runbooks, security-sensitive docs, or a user request for exhaustive review | Build a claim and documentation-impact map, validate high-risk examples and procedures, inspect related docs and contracts, independently re-check candidates, and record coverage gaps. Cap at fifteen findings. |

At any tier, assess risk before deciding depth. Setup, deployment, migration, security,
destructive-operation, and public-contract instructions require more evidence than a
low-impact overview.

## Gather context before judging

1. Read applicable repository guidance, contribution and docs conventions, nearby READMEs,
   and audience-specific instructions.
2. Identify each document's purpose, intended reader, lifecycle, and authority:
   current reference, tutorial, operational runbook, design proposal, historical ADR, generated
   output, or external/vendor material.
3. Identify evidence that can establish its claims: tests, public interfaces, implementation,
   schemas, configuration defaults, build files, package metadata, examples, CI, design records,
   and history where needed.
4. Search exact identifiers plus concepts, old/new terms, paths, option values, error messages,
   and related workflows. A negative exact-name search alone does not prove that no relevant
   documentation exists.
5. For a change-set review, read enough surrounding code, tests, and configuration to explain
   the semantic change rather than merely restating edited lines.

Do not inspect the entire repository by default. Read evidence proportional to the claim and
record material areas that could not be checked.

## Apply the evidence rule

Never assess a technically verifiable claim in isolation when repository evidence is available.

For **current behavior**, prefer evidence in this order when applicable:

1. tests that demonstrate externally observable behavior or contractual invariants;
2. current public interfaces and implementation;
3. schemas, configuration definitions/defaults, build metadata, and package manifests;
4. working examples and CI workflows;
5. current documentation.

For **intent or rationale**, prefer accepted design records, specifications, contractual tests,
issue context present in the repository, and history. Do not invent rationale from an
implementation detail.

Code does not automatically win a conflict. When implementation, test, contract, and
documentation disagree, describe what each source establishes and surface the unresolved
code-versus-contract decision. Do not silently rewrite documentation to encode potentially
accidental behavior.

Preserve historical truth. An ADR, proposal, changelog, or release note is not stale merely
because the software later changed; flag it only when it presents historical material as current
or violates its stated lifecycle.

## Review workflow

### 1. Build a claim map

Identify material claims and classify them as:

- factual/current behavior;
- instructional or executable procedure;
- contractual API/configuration promise;
- architecture or operational statement;
- rationale/decision history; or
- reader-navigation and discoverability information.

Focus tracing effort on claims where being wrong would cause a failed setup, misuse, data loss,
security exposure, incompatible integration, outage, or materially incorrect design decision.

### 2. Verify claims and executable material

Trace important claims into the evidence identified above. For commands, snippets,
configuration, and workflows, check as many of these as apply:

- prerequisites, supported versions, permissions, and working directory;
- command syntax, flags, paths, environment variables, and generated artifacts;
- sequence, expected intermediate result, failure handling, and cleanup;
- API signatures, parameter/return/error semantics, ownership, ordering, concurrency, and
  compatibility promises;
- safety of destructive or privileged operations.

Run non-destructive examples, focused tests, builds, linters, link checks, or project-provided
documentation validation when practical and safe. If execution is not practical, inspect the
actual command wiring and label the verification as static rather than claiming it ran.

### 3. Check completeness and cross-document consistency

Ask whether the intended reader has the information needed to succeed, including prerequisites,
defaults, constraints, failure modes, and newly relevant behavior. Search related documentation
for contradictory terminology, APIs, option values, instructions, and architecture descriptions.

Check discoverability when a fact is necessary at a decision or action point: a correct fact
hidden in an unrelated document can still be a reader-blocking omission.

### 4. Build a documentation-impact map for changes

For each semantic implementation change, determine whether it affects:

- public APIs, data models, errors, ordering, lifetime, or compatibility;
- commands, flags, configuration, environment variables, defaults, paths, or output;
- installation, build, deployment, migration, troubleshooting, operation, or rollback;
- architecture boundaries, control/data flow, extension points, or critical constraints;
- examples, tutorials, reference material, or safety guidance.

Search for exact and conceptual references. Mark relevant documentation as `updated`,
`needs change`, `verified unaffected`, or `not found`. Ignore implementation-only refactors
unless they alter an architecture fact that readers are expected to rely on.

### 5. Decide whether to edit

In synchronization mode:

- make the smallest complete change that restores a verified contract or workflow;
- update materially affected examples, cross-references, and safety notes together;
- remove or clearly deprecate removed behavior;
- preserve project terminology and local documentation style;
- avoid unrelated rewriting and never edit generated, vendored, or externally sourced material
  unless repository guidance requires it;
- update the status or add a successor for historical decisions rather than rewriting their past.

In review modes, provide concrete proposed corrections without modifying files.

### 6. Re-verify

After synchronization or while finalizing a review:

1. Re-read changed or reviewed instructions as the target reader would use them.
2. Re-check each changed factual claim against evidence.
3. Re-run practical validation for changed executable material.
4. Search for stale old terms, values, paths, and contradictory statements left elsewhere.
5. Check affected local links, anchors, and references.
6. Review the final documentation diff for scope and accidental claims.

## Finding quality and severity

Only report findings with concrete reader impact and repository evidence. Each material finding
needs a severity, drift type, documentation location, evidence location, impact, and smallest
complete fix. Use an open question for ambiguity that could change the conclusion, rather than
presenting speculation as a defect.

Use the severity definitions in the rubric:

- `critical`: unsafe instructions, likely data loss, severe security exposure, or major outage;
- `high`: primary workflow or important contract is wrong or cannot succeed;
- `medium`: material misinformation or omission likely to produce incorrect integration,
  operation, or debugging decisions, with a workaround;
- `low`: real but limited reader cost;
- suppress `nit` findings by default.

Do not report a style preference, an unchanged unrelated document, or a hypothetical gap with no
reasonable evidence that readers need the claimed information.

## Output and handoff

Use `<SKILL_ROOT>/references/review-report-template.md` unless the user requested another
format. Findings are primary; keep process narration short. State only checks actually
performed and clearly distinguish executed, statically inspected, skipped, and blocked checks.

If no material findings are discovered, say so clearly, summarize the main evidence checked, and
name meaningful residual coverage limits.

Route work deliberately:

- A code defect exposed by documentation evidence belongs to **code-reviewer**, followed by
  implementation or debugging as appropriate.
- Missing or stale documentation after a code review belongs to this skill's synchronization
  workflow.
- A broad behavioral change needing coordinated code and docs work may need
  [../plan-guide/SKILL.md](../plan-guide/SKILL.md) or
  [../plan-executor/SKILL.md](../plan-executor/SKILL.md) after the findings are accepted.

## Companion Skills

| Task | Path |
| --- | --- |
| Code diff review and implementation defects | [../code-reviewer/SKILL.md](../code-reviewer/SKILL.md) |
| Author or revise tutorials and user guides | [../tutorial-writer/SKILL.md](../tutorial-writer/SKILL.md) |
| Learn or explain existing code without doc review | [../code-professor/SKILL.md](../code-professor/SKILL.md) |
| PR description and self-review narrative | [../pull-request-guide/SKILL.md](../pull-request-guide/SKILL.md) |
| Coordinated code and docs implementation | [../plan-guide/SKILL.md](../plan-guide/SKILL.md), [../plan-executor/SKILL.md](../plan-executor/SKILL.md) |
| Root-cause repair when docs expose a code defect | [../debugging-guide/SKILL.md](../debugging-guide/SKILL.md) |

## Completion quality bar

Before finishing, confirm that:

- material findings are evidence-backed and severity reflects reader impact;
- current behavior, intended contract, and historical documentation were not conflated;
- executable examples were validated or honestly labeled as unexecuted;
- semantic drift was considered even if names did not change;
- related documents were searched where a cross-document conflict is plausible;
- synchronization edits are conservative, complete for the affected contract, and scoped; and
- unresolved evidence conflicts and verification limits are explicit.
