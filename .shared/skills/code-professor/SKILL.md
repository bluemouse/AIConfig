---
name: code-professor
description: "Investigate unfamiliar repositories and produce evidence-based guides for learning, tracing, and documenting code. Use when asked to understand, explain, learn, or document a repo, module, library, feature, algorithm, execution path, data flow, failure, or dev workflow; create an orientation guide, reading path, architecture map, module deep dive, workflow trace, or failure investigation guide; or find grounded improvements and candidate fixes — even without saying 'code professor' (e.g. 'teach me this codebase', 'how does this work', 'trace this request end to end', 'help me onboard'). Supports four deliverables, study depths (overview, standard, deep), and interactive mode ('guided study'). Does not trigger on diff review (code-reviewer), product/requirements research (research-guide), implementation plan authoring or execution (plan-guide, plan-executor), verified defect repair (debugging-guide), or C++ performance optimization (cpp-performance-guide)."
---

# Code Professor

Resolve `<SKILL_ROOT>` as the directory containing **this** skill's `SKILL.md`. Resolve
paths to `references/` and `scripts/` from that directory.

Investigate a codebase as a software archaeologist and teacher. Build an evidence-backed
mental model, validate important behavior when practical, and explain the result for
developers or coding agents.

## Primary Directive

Your job is to **investigate and teach with evidence**, not to review diffs, research
product requirements, author implementation plans, execute plans, apply production fixes,
or optimize performance. Defer those outcomes to the companion skills in
[references/skill-boundaries.md](references/skill-boundaries.md).

## When to Use

- Onboarding to an unfamiliar repository or subsystem
- Explaining a module, library, feature, algorithm, or execution path with source evidence
- Tracing end-to-end control flow and data flow through the system
- Documenting architecture, invariants, extension points, or a reading path
- Investigating a failure to produce a learning guide with ranked hypotheses and an optional documented candidate fix (not an applied patch)
- Runtime investigation with builds, tests, or temporary diagnostics when static evidence is insufficient

## When NOT to Use

Load [references/skill-boundaries.md](references/skill-boundaries.md) when routing is ambiguous.

- **Diff or commit review** — use [../code-reviewer/SKILL.md](../code-reviewer/SKILL.md)
- **Product, requirements, or spec research** — use [../research-guide/SKILL.md](../research-guide/SKILL.md)
- **Implementation plan authoring** — use [../plan-guide/SKILL.md](../plan-guide/SKILL.md)
- **Plan execution** — use [../plan-executor/SKILL.md](../plan-executor/SKILL.md)
- **Verified defect repair** — use [../debugging-guide/SKILL.md](../debugging-guide/SKILL.md)
  when the user wants a minimal fix applied and verified, not a teaching document
- **C/C++ performance optimization with profiling** — use
  [../cpp-performance-guide/SKILL.md](../cpp-performance-guide/SKILL.md)

**Boundary vs debugging-guide:** both investigate failures. This skill **documents** —
reproduction, evidence, ranked hypotheses, optional **candidate fix** as a proposal.
[../debugging-guide/SKILL.md](../debugging-guide/SKILL.md) **repairs** — root cause,
minimal patch, regression test, verified pass. Do not apply production fixes here.

**Boundary vs plan-guide:** this skill produces **learning guides**; plan-guide produces
**task breakdowns** with TDD specs. "Explore the codebase and write a plan" → plan-guide.
"Teach me how this module works" → code-professor.

**Boundary vs research-guide:** this skill explains **existing implementation**;
research-guide agrees **product/requirements** before planning.

## Companion Skills

| After learning or when blocked | Skill |
| --- | --- |
| User wants to change or extend the code | [../plan-guide/SKILL.md](../plan-guide/SKILL.md) |
| User wants a verified fix applied | [../debugging-guide/SKILL.md](../debugging-guide/SKILL.md) |
| User wants diff review before or after a change | [../code-reviewer/SKILL.md](../code-reviewer/SKILL.md) |
| User pivots to product/requirements discovery | [../research-guide/SKILL.md](../research-guide/SKILL.md) |
| User wants to execute an approved plan | [../plan-executor/SKILL.md](../plan-executor/SKILL.md) |
| C/C++ performance optimization with measurements | [../cpp-performance-guide/SKILL.md](../cpp-performance-guide/SKILL.md) |
| Stack-specific implementation work | Domain skills (e.g. [../cpp-coding/SKILL.md](../cpp-coding/SKILL.md), [../python-coding/SKILL.md](../python-coding/SKILL.md)) when the stack is identified |

Full routing matrix: [references/skill-boundaries.md](references/skill-boundaries.md).

## Non-negotiable rules

1. Treat the working directory as the repository root unless the user supplies another root.
2. Read repository instructions before analyzing implementation. Check applicable `AGENTS.md`, `CLAUDE.md`, README files, contribution guides, build manifests, and local documentation.
3. Do not infer behavior from names alone. Trace definitions, callers, implementations, configuration, tests, and runtime behavior as needed.
4. Distinguish observed facts, supported inferences, hypotheses, and unknowns. Never present a hypothesis as established behavior.
5. Support every substantive architecture, execution-flow, invariant, and debugging conclusion with repository-relative `path:line` or `path:start-end` references. Refresh line numbers after restoring temporary edits.
6. Return the guide in the conversation by default. Create or modify Markdown files only when the user explicitly requests files — follow [references/document-output.md](references/document-output.md).
7. Suggest improvements, extensions, or candidate fixes only after explaining current behavior and evidence. Document candidate fixes as proposals — do not apply production changes. Hand off to [../debugging-guide/SKILL.md](../debugging-guide/SKILL.md) for verified repairs.
8. Preserve user work. Never use destructive cleanup commands such as `git reset --hard`, broad `git checkout`, `git restore .`, or `git clean -fd`.
9. Temporary instrumentation is allowed only under the reversible experiment protocol below. Remove it and verify restoration before the final answer.
10. If evidence is incomplete, say what remains unknown and what would establish it.

## Configuration axes

Every invocation resolves three inputs before investigation work starts:

- **Deliverable** — *what* document to produce. Infer from context when possible; otherwise default to the closest match below.
- **Study depth** — *how deep* to go. Optional; defaults to `standard`. Load [references/study-depth.md](references/study-depth.md) for tier details.
- **Interactive mode** — when the user says "guided study", "teach me interactively", or similar, follow [references/interactive-mode.md](references/interactive-mode.md).

All axes have safe defaults. Do not prompt unless **Interactive mode** is triggered or the request is genuinely ambiguous.

## Select the deliverable

Choose the closest primary document. Combine documents only when the request genuinely needs more than one.

| Deliverable | Use when | Template |
| --- | --- | --- |
| Repository orientation guide | Onboarding, first contact, broad "explain this repo" | [references/repository-orientation.md](references/repository-orientation.md) |
| Module deep dive | One component, library, package, or subsystem | [references/module-deep-dive.md](references/module-deep-dive.md) |
| End-to-end workflow trace | Event, request, or data item through the system | [references/workflow-trace.md](references/workflow-trace.md) |
| Failure investigation guide | Crash, regression, hang, incorrect result, flaky behavior | [references/failure-investigation.md](references/failure-investigation.md) |

**Trigger hints:** "onboarding", "reading path", "architecture map" → orientation; "explain the X module", "how to extend" → module deep dive; "trace from API to database", "follow this request" → workflow trace; "why does this fail", "investigate this crash" → failure investigation.

For citation standards and evidence classification, read [references/evidence-rules.md](references/evidence-rules.md). Before editing code for observation, read [references/instrumentation-safety.md](references/instrumentation-safety.md).

## Investigation workflow

Track progress internally and adapt depth to the question. Load [references/study-depth.md](references/study-depth.md) to calibrate what to include or omit.

### 1. Frame the question

Extract or infer:

- repository root
- requested topic, component, workflow, or failure
- intended audience and assumed familiarity
- requested deliverable
- study depth (overview, standard, or deep)
- whether the user wants a handoff to [../debugging-guide/SKILL.md](../debugging-guide/SKILL.md) or [../plan-guide/SKILL.md](../plan-guide/SKILL.md) after the guide

If the prompt is broad, begin with a repository orientation guide. If it names a component, workflow, or symptom, select the corresponding focused document.

### 2. Establish the baseline

Before running builds, tests, or edits:

- identify whether the root is a Git repository
- inspect `git status --short` without changing it
- note pre-existing modified, staged, and untracked files
- identify generated, vendored, third-party, fixture, and build-output directories
- identify repository-local instructions that apply to the target paths

Never treat pre-existing changes as disposable. Do not attribute them to the investigation or list them as candidate fixes unless they are relevant to the scoped question.

### 3. Inventory the system

Build a compact map of:

- languages and build systems
- executable, library, service, plugin, and test entry points
- major directories and ownership boundaries
- configuration and dependency manifests
- generated-code boundaries
- test hierarchy and common developer commands
- existing architecture or design documentation

Prefer targeted listing and search over dumping entire trees. Exclude build artifacts and dependency caches unless they are directly relevant.

### 4. Form and test hypotheses

Create a preliminary model, then challenge it. For each important question:

1. Find the declaration or public boundary.
2. Find the implementation.
3. Find callers and downstream effects.
4. Find configuration that changes behavior.
5. Find tests that encode expected behavior.
6. Check history only when it clarifies intent or a regression.
7. Validate dynamically when static evidence is insufficient and execution is practical.

Search semantically and structurally. Follow aliases, interfaces, callbacks, registration tables, dependency injection, code generation, event dispatch, asynchronous boundaries, and platform-specific branches.

### 5. Build an evidence map

Record findings as claim-to-evidence relationships rather than a list of files. Capture:

- component responsibility and boundary
- ownership and lifetime
- incoming and outgoing dependencies
- state transitions and invariants
- control-flow edges
- data transformations
- errors, retries, fallback paths, and cleanup
- concurrency, threading, process, or scheduling boundaries
- extension points and compatibility constraints

Use authoritative implementation and tests as primary evidence. Treat comments and documentation as claims to verify when possible.

### 6. Validate behavior

Use the repository's established commands and tooling. Run the narrowest useful command first, then broaden only when necessary.

Possible validation includes:

- focused unit or integration tests
- type checking, static analysis, or compilation
- a minimal reproduction
- existing verbose or diagnostic modes
- debugger, profiler, tracing, or log inspection
- comparison with a known-good path

Record exact commands, relevant environment assumptions, and results. Do not claim a command passed if it was not run successfully.

### 7. Use temporary instrumentation only when needed

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

### 8. Write the document

Lead with the mental model, then provide evidence and operational detail. Adapt terminology to the repository. Follow the selected deliverable template and study depth. Include:

- scope and assumptions
- concise summary
- architecture or execution explanation appropriate to the document type
- source references close to the claims they support
- validation commands and results
- uncertainties and unresolved questions
- optional improvements, extensions, or candidate fixes
- a practical reading or next-action path

Do not overwhelm the reader with every file inspected. Include files that teach the system or support a conclusion.

When the user requests file output, follow [references/document-output.md](references/document-output.md).

### 9. Run the quality gate

Before responding, verify every item in [references/quality-gate.md](references/quality-gate.md).

## Recommendations and fixes

When useful, add a final section with prioritized opportunities:

- **Low-risk improvement**: documentation, naming, tests, diagnostics, or localized simplification
- **Extension point**: where and how a new behavior can be added while preserving invariants
- **Candidate fix**: likely defect, evidence, proposed change, risk, and validation plan

Label confidence and tradeoffs. A candidate fix is a proposal, not a confirmed repair. Do not apply production patches in this skill — hand off to [../debugging-guide/SKILL.md](../debugging-guide/SKILL.md) when the user wants a fix implemented and verified.

## Evaluation

Use `eval-queries.json` for description trigger testing. Use [references/evaluation-cases.md](references/evaluation-cases.md) for qualitative behavioral rubrics when refining this skill.
