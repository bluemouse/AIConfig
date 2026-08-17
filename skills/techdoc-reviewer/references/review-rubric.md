# Technical Documentation Review Rubric

Use this reference to decide what to verify, classify documentation drift, and assign
severity. Apply only dimensions relevant to the document's purpose and audience.

## Primary invariant

Documentation drift exists when a reasonable reader could form an incorrect or materially
incomplete model of the currently supported software. Drift includes both false statements and
missing information needed to use, operate, integrate with, or safely change the software.

The most important review question is not "is this well written?" but "will the intended reader
make a correct decision and successfully complete the task?"

## Drift taxonomy

| Type | What to detect |
| --- | --- |
| Contradiction | A current document explicitly conflicts with verified current behavior. |
| Omission | Reader-relevant behavior, constraint, prerequisite, option, or failure handling is absent. |
| Removal | Documentation still presents a removed API, command, component, file, or workflow as supported. |
| Rename | Documentation uses an obsolete current name for a code, configuration, CLI, or architecture concept. |
| Semantic | The name remains, but its lifetime, ordering, blocking, error, ownership, compatibility, or other contract changes. |
| Example | A snippet, command, sample config, expected output, or text-described screenshot no longer represents supported use. |
| Workflow | Setup, build, deployment, migration, diagnosis, recovery, or release steps no longer work in order. |
| Architecture | Components, boundaries, dependencies, control/data flow, invariants, ownership, or extension points are obsolete or misleading. |
| Default/configuration | Defaults, precedence, paths, flags, environment variables, values, or compatibility rules diverge. |
| Discoverability | Critical information exists but is missing at the reader's decision or action point. |
| Safety/security | Instructions weaken permissions, expose credentials, disable protection, perform destructive actions unsafely, or omit required safeguards. |

Give special attention to semantic drift. For APIs and concurrent or resource-sensitive systems,
verify sync versus async completion, ownership/lifetime, ordering, thread safety, blocking,
error semantics, side effects, initialization/shutdown, persistence/caching, and
performance-sensitive guarantees.

## General review dimensions

### Technical correctness

Verify names, signatures, defaults, values, constraints, procedures, dependencies, and
observable behavior against current repository evidence.

### Completeness and audience fit

Check that the intended reader has prerequisite knowledge, tools, permissions, configuration,
decision criteria, expected results, and relevant edge/failure cases. Do not require internal
implementation details unless the audience needs them to use or operate the system correctly.

### Executability

Validate commands, snippets, config, and procedural sequences where safe. Check working
directory, inputs, generated files, environment, permissions, version assumptions, expected
results, cleanup, and rollback. A command that parses but requires an undocumented prerequisite
is not a successful example.

### Cross-document consistency and discoverability

Search related docs for contradicting terms, defaults, contracts, and procedures. Prefer a
canonical reference plus links over duplicating fast-changing facts in several places. Treat
links and anchors as part of the workflow: they must resolve to the intended current material.

### Architecture and rationale

For architecture material, verify responsibilities, dependency direction, control/data flow,
invariants, ownership, extension points, and meaningful portability/performance limits. Require
rationale only when the document's purpose is design understanding; never infer undocumented
intent from code alone.

### Operations, failure, and safety

For operational docs, verify diagnosis, safe commands, expected signals, recovery, rollback,
escalation, logging/monitoring references, and dangerous-operation guardrails. Treat unsafe or
irreversible advice as high risk even when the happy path is correct.

### Clarity and maintainability

Flag ambiguity, undefined terms, misleading organization, or duplicated volatile information
only when it changes technical meaning, blocks action, or creates a credible maintenance risk.
Suppress grammar and stylistic preferences unless requested.

## Document-type focus

### README and getting started

Verify project scope, supported environments, prerequisites, a reproducible first successful
result, command working directories, and links to deeper reference material.

### Build, install, and setup

Verify tool/runtime versions, dependency discovery, environment variables, platform differences,
commands, generated artifacts, expected outputs, and troubleshooting for common failure modes.

### API and configuration reference

Verify signatures/types, parameters, return values, errors, defaults, valid values, precedence,
ownership/lifetime, thread safety, ordering, initialization/shutdown, deprecation, compatibility,
and examples.

### Architecture guide

Verify current components and their responsibilities, dependency direction, data/control flow,
lifecycles, invariants, extension points, and whether current state and future proposals are
clearly labeled.

### ADR, proposal, or design record

Verify status, context, constraints, alternatives, decision, rationale, and consequences.
Preserve the historical decision; record supersession or changed status instead of rewriting
past context as though it were current architecture.

### Tutorial or migration guide

Verify the starting state, complete sequence, current APIs/commands, expected intermediate
results, hidden prerequisites, rollback/cleanup, and next steps. Migration guidance also needs
version boundaries, compatibility implications, and a safe recovery path.

### Runbook and troubleshooting guide

Verify trigger conditions, diagnosis steps, least-risk commands, expected signals, permissions,
rollback/recovery, escalation, and stale service/tool/path names. Confirm that emergency actions
are distinguishable from normal operation.

## Severity rubric

| Severity | Reader impact |
| --- | --- |
| `critical` | Plausible severe security exposure, destructive action, data loss, major outage, or fundamentally unsafe operation. |
| `high` | A primary documented workflow cannot succeed, an important public/operational contract is materially wrong, or a required prerequisite or constraint is absent and likely blocks users. |
| `medium` | A material ambiguity, omission, inconsistency, or semantic mismatch can cause incorrect integration, implementation, debugging, or operations, but a workaround normally exists. |
| `low` | Limited but real discoverability, terminology, maintainability, or clarity cost. |
| `nit` | Grammar or preference with no material technical impact; suppress by default. |

Do not inflate severity merely because a claim is technically wrong. Classify the likely harm to
the reader who follows it.

## Evidence and conflict rules

### Current behavior

Prefer, in order where applicable:

1. tests that demonstrate observable behavior or explicit invariants;
2. public definitions and current implementation;
3. schemas, configuration, build metadata, and package manifests;
4. working examples and CI workflows;
5. current documentation.

### Intent and historical context

Use accepted specifications, ADRs, contractual tests, comments, issue context available in the
repository, and history. Old design records establish what was decided then; they do not, by
themselves, establish current behavior.

### Conflicts and absence

When strong sources disagree:

1. state the conflicting sources and what each establishes;
2. distinguish behavior from intended contract;
3. do not choose the easiest document edit as the resolution; and
4. recommend the responsible owner resolve the discrepancy when intent remains unclear.

When evidence is absent, use `unverified` or an open question. A failed exact-name search is
weak negative evidence: also search old/new terms, synonyms, conceptual references, and related
workflows before asserting a documentation gap.

## Finding examples

### High — semantic drift

**Location:** `docs/rendering-api.md`, `Renderer::submit`

**Finding:** The document says `submit()` completes GPU work before returning, but the current
contract queues work asynchronously.

**Evidence:** The implementation returns after queue submission; the returned fence is the
synchronization primitive, and the updated test waits on it.

**Impact:** Callers following the docs may reuse or destroy resources before GPU completion.

**Recommended fix:** Describe asynchronous completion and the required fence wait/lifetime rule;
update examples that assume blocking behavior.

### Medium — configuration omission

**Location:** `docs/configuration.md`, present-mode options

**Finding:** The option table omits newly supported `Mailbox`.

**Evidence:** The config enum, parser, and validation test accept `Immediate`, `FIFO`, and
`Mailbox`.

**Impact:** Users cannot discover or confidently select the supported mode.

**Recommended fix:** Add `Mailbox`, describe its behavior, and state the default only if the
repository establishes one.
