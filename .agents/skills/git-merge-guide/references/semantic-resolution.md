# Semantic conflict resolution

Treat complex conflict resolution as debugging an integration regression.

## Contents

- [Resolution objective](#resolution-objective)
- [Form a hypothesis](#form-a-hypothesis)
- [Choose a resolution mode](#choose-a-resolution-mode)
- [Common bug patterns after mechanical merges](#common-bug-patterns-after-mechanical-merges)
- [Tests as investigation tools](#tests-as-investigation-tools)
- [Generated and derived state](#generated-and-derived-state)
- [User decision gate](#user-decision-gate)
- [Decision format](#decision-format)

## Resolution objective

Produce the behavior that would plausibly have been written if both sets of requirements had been known when the code was authored. Preserve the intentions supported by local evidence, not the original textual shapes.

Do not optimize for minimal diff if minimal text produces incorrect behavior. Do not perform broad opportunistic refactors unrelated to integration.

## Form a hypothesis

Before editing, write an internal resolution statement such as:

> Keep the new resource-lifetime model from A, preserve B's deferred upload behavior, and adapt B to acquire the resource through the new owner so deferred work cannot retain a stale pointer.

A good hypothesis names behavior and invariants, not lines to keep.

## Choose a resolution mode

### 1. Adopt one implementation

Use when history/code clearly shows one change supersedes the other, or one side is purely mechanical and the other already contains its effect. Verify that no distinct behavior is lost.

### 2. Compose independent changes

Integrate both when they modify different concerns. Re-check control flow, ordering, initialization, cleanup, and error handling after composition.

### 3. Adapt a sequential change

Common during rebase: the replayed commit was written against an older API. Preserve its intent but rewrite it to use the upstream/current architecture rather than restoring removed abstractions just to match the old patch.

### 4. Rewrite the implementation

Use when line-by-line merging would duplicate work, violate invariants, or create fragile control flow. Keep the rewrite scoped to the logical integration problem. Reuse repository idioms and tests.

### 5. Change neighboring non-conflicted code

Do this when integration requires caller/type/test/config updates that Git did not flag. Explain these changes in the final summary because they are semantic merge fixes, not textual conflict resolutions.

## Common bug patterns after mechanical merges

Actively check for:

- duplicate side effects because both branches added similar calls;
- dropped validation/error handling from one side;
- stale API calls that still compile through overload/default behavior;
- inverted ownership or lifetime assumptions;
- double-free, leak, stale reference, or invalid iterator risks;
- changed execution ordering;
- missing synchronization or lock-order changes;
- initialization performed twice or no longer performed;
- cleanup paths that only match one branch's resource model;
- inconsistent units, coordinate spaces, ranges, enum meanings, or sentinel values;
- serializers/readers using different schema versions;
- feature gating applied on only one path;
- tests merged mechanically so they no longer test the original regression.

## Tests as investigation tools

Use tests to distinguish hypotheses, not merely to obtain a green build.

When possible:

1. Locate tests changed by each conflicting commit.
2. Understand which regression/feature each test protects.
3. Preserve both sets when their requirements remain valid.
4. Add or adapt a focused integration test when neither existing test exercises the interaction.
5. If a test fails because the two intentions are incompatible, do not weaken/delete it simply to pass; investigate and ask when necessary.

## Generated and derived state

If conflict resolution changes a source-of-truth schema, generated API, shader/interface declaration, build metadata, lockfile, or codegen input, regenerate derived files using the repository's local tooling where practical. Verify generated diffs are attributable to the source change.

## User decision gate

Ask when code/history cannot determine which behavior is intended. Typical triggers:

- both sides intentionally implement different product semantics;
- a deletion could mean replacement or abandonment and no local evidence distinguishes them;
- two APIs encode incompatible ownership/threading/lifetime models;
- a test documents one behavior while later code deliberately appears to implement another, with no clear superseding evidence;
- preserving both behaviors requires choosing a policy, precedence, fallback, performance/correctness trade-off, compatibility break, or externally observable behavior;
- any resolution would knowingly discard a distinct intention.

Do not ask merely because the conflict is difficult. Research first.

## Decision format

Use a concise structure:

**Decision:** Describe the unresolved semantic question.

**Evidence:** Summarize the relevant local commits/code/tests for each interpretation.

**Options:**
- **A - ...:** behavior and consequence.
- **B - ...:** behavior and consequence.
- **C - ...:** combined/rewrite approach when plausible.

**Recommendation:** Choose the best-supported option and explain why.

**Question:** Ask the user for the missing intent or option selection.

Do not stage a speculative version of this logical conflict while waiting for the decision.
