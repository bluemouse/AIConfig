---
name: code-professor
description: "Investigate unfamiliar codebases and produce evidence-backed learning guides — repository orientation, architecture maps, module deep dives, end-to-end workflow traces, failure-investigation guides, or interactive guided study ('teach me this codebase', 'how does this work', 'help me onboard'). Not for diff review (code-reviewer), product research (research-guide), implementation planning/execution, or defect repair (debugging-guide)."
---

# Code Professor

Resolve `<SKILL_ROOT>` as the directory containing **this** skill's `SKILL.md`. Investigate
a codebase as a software archaeologist and teacher: build an evidence-backed mental
model, validate important behavior when practical, and explain it for developers or
coding agents.

## When NOT to Use

- **Diff or commit review** — [../code-reviewer/SKILL.md](../code-reviewer/SKILL.md); code-professor studies baseline code, code-reviewer needs a change set
- **Product, requirements, or spec research** — [../research-guide/SKILL.md](../research-guide/SKILL.md); code-professor covers settled implementation with `path:line` evidence, research-guide covers unsettled requirements
- **Implementation plan authoring** — [../plan-guide/SKILL.md](../plan-guide/SKILL.md); "explore the codebase and turn this ask into a plan" is plan-guide even when it reads code
- **Plan execution** — [../plan-executor/SKILL.md](../plan-executor/SKILL.md)
- **Verified defect repair** (applied fix, not a teaching document) — [../debugging-guide/SKILL.md](../debugging-guide/SKILL.md); "investigate this crash" / "why does this fail" is code-professor until the user asks for a patch applied
- **C/C++ performance optimization with profiling** — [../cpp-performance-guide/SKILL.md](../cpp-performance-guide/SKILL.md); "why is this path slow?" is a code-professor failure investigation, "profile and optimize it" is cpp-performance-guide

## Non-negotiable rules

1. Treat the working directory as the repository root unless the user supplies another root. Read repository instructions (`AGENTS.md`, `CLAUDE.md`, READMEs, build manifests, local docs) before analyzing implementation.
2. Do not infer behavior from names alone. Trace definitions, callers, implementations, configuration, tests, and runtime behavior as needed.
3. Never treat pre-existing working-tree changes as disposable; do not use destructive cleanup (`git reset --hard`, broad `git checkout`, `git clean -fd`) or attribute pre-existing changes to the investigation.
4. Distinguish observed facts, supported inferences, hypotheses, and unknowns. Never present a hypothesis as established behavior.
5. Support every substantive architecture, execution-flow, invariant, and debugging conclusion with repository-relative `path:line` or `path:start-end` references. Refresh line numbers after restoring temporary edits.
6. Return the guide in the conversation by default; create or modify Markdown files only when the user explicitly requests files — follow [references/document-output.md](references/document-output.md). Candidate fixes are proposals only; hand off to [../debugging-guide/SKILL.md](../debugging-guide/SKILL.md) for verified repairs.
7. Temporary instrumentation is allowed only under the reversible experiment protocol below. Remove it and verify restoration before the final answer.
8. If evidence is incomplete, say what remains unknown and what would establish it.

## Configuration axes

Resolve before investigation starts; all have safe defaults — do not prompt unless the
request is genuinely ambiguous (then [../prompt-clarifier/SKILL.md](../prompt-clarifier/SKILL.md)):

- **Deliverable** — *what* document; infer from context, default to the closest match below.
- **Study depth** — *how deep*; defaults to `standard`. Details: [references/study-depth.md](references/study-depth.md).
- **Interactive mode** — "guided study", "teach me interactively": [references/interactive-mode.md](references/interactive-mode.md).

## Select the deliverable

| Deliverable | Use when | Template |
| --- | --- | --- |
| Repository orientation guide | Onboarding, first contact, broad "explain this repo" | [references/repository-orientation.md](references/repository-orientation.md) |
| Module deep dive | One component, library, package, or subsystem | [references/module-deep-dive.md](references/module-deep-dive.md) |
| End-to-end workflow trace | Event, request, or data item through the system | [references/workflow-trace.md](references/workflow-trace.md) |
| Failure investigation guide | Crash, regression, hang, incorrect result, flaky behavior | [references/failure-investigation.md](references/failure-investigation.md) |

Combine documents only when the request genuinely needs more than one.

## Investigation workflow

Frame first (root, topic, audience, depth, requested handoff), then:

- Note `git status --short` and pre-existing modified/staged/untracked files before running builds, tests, or edits; identify generated, vendored, fixture, and build-output directories.
- Inventory compactly: languages, build system, entry points, directory boundaries, manifests, test hierarchy, developer commands, existing architecture docs. Prefer targeted search over dumping trees.
- Form a preliminary model, then challenge it: declaration → implementation → callers → configuration → tests → history (only for intent or regression questions). Follow aliases, callbacks, registration tables, DI, code generation, event dispatch, async boundaries.
- Record findings as claim-to-evidence relationships, not file lists. Implementation and tests are primary evidence; comments and docs are claims to verify. Citation standards: [references/evidence-rules.md](references/evidence-rules.md).
- Validate when static evidence is insufficient and execution is practical: narrowest useful command first, then broaden. Record exact commands and results — never claim a command passed if it did not.
- Only for `deep`-depth orientation guides on large repositories: dispatch read-only per-directory exploration via [../agent-runner/SKILL.md](../agent-runner/SKILL.md); keep hypothesis formation and the final mental model in the parent context.

### Use temporary instrumentation only when needed

Prefer existing logs, tests, debuggers, and tracing facilities. If those cannot answer the question, perform a reversible experiment:

1. Select the smallest set of files to edit.
2. Snapshot each selected path with `<SKILL_ROOT>/scripts/instrumentation_guard.py` before editing — see [references/instrumentation-safety.md](references/instrumentation-safety.md).
3. Mark temporary code clearly with `CODE_PROFESSOR_TEMP`.
4. Avoid secrets, credentials, personal data, and excessive logging.
5. Run only the experiment needed to answer the question.
6. Restore exact original contents with the guard script.
7. Verify the guarded paths match their snapshots.
8. Re-run `git status --short` and inspect diffs against the baseline.
9. Delete the external snapshot only after verification succeeds.

If restoration or verification fails, stop and report the affected paths. Do not claim the investigation is complete.

### Write the document

Lead with the mental model, then evidence and operational detail. Follow the selected deliverable template and study depth — the templates in `references/` specify the required structure, including any recommendations/candidate-fix section; label confidence and tradeoffs. For file output, follow [references/document-output.md](references/document-output.md). Before responding, verify every item in [references/quality-gate.md](references/quality-gate.md).
