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

Review each document for technical correctness against repository evidence, completeness
for its intended audience, executability of its commands and procedures (working
directory, inputs, environment, version assumptions, expected results, cleanup), and
cross-document consistency (contradicting terms/defaults/procedures; canonical reference
plus links over duplicated fast-changing facts; links resolve to current material). Apply
only the dimensions relevant to the document's purpose and audience. Suppress grammar and
stylistic preferences unless requested.

## Document-type focus

For the document's type, check what its reader will act on: README/getting-started
(environment, prerequisites, a reproducible first success), build/install/setup (versions,
environment, artifacts, common failure modes), API/configuration reference (signatures,
defaults, precedence, ownership/lifetime, compatibility, examples), architecture guide
(components, dependency direction, invariants, current vs proposed state), ADR (status,
rationale, consequences — preserve the historical decision; record supersession rather
than rewriting past context as current), tutorial/migration guide (starting state,
sequence, hidden prerequisites, rollback, version boundaries), runbook (trigger
conditions, least-risk commands, recovery, escalation, distinguishable emergency
actions).

## Severity rubric

| Severity | Reader impact |
| --- | --- |
| `blocker` | Plausible severe security exposure, destructive action, data loss, major outage, or fundamentally unsafe operation. |
| `major` | A primary documented workflow cannot succeed, an important public/operational contract is materially wrong, or a required prerequisite or constraint is absent and likely blocks users. |
| `minor` | A material ambiguity, omission, inconsistency, or semantic mismatch can cause incorrect integration, implementation, debugging, or operations, but a workaround normally exists. |
| `nit` | Limited but real discoverability, terminology, maintainability, or clarity cost. |
| `nit` (suppress) | Grammar or preference with no material technical impact; suppress by default. |

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
