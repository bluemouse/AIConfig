# Integration code review

Perform this review only after all Git conflicts are resolved and each conflict has passed its focused checks. The purpose is to find semantic integration bugs in code Git merged cleanly, plus interactions introduced by conflict resolutions.

## Contents

- [Review objective](#review-objective)
- [Build stable comparison sets](#build-stable-comparison-sets)
- [Build an interaction map](#build-an-interaction-map)
- [Required bug classes to review](#required-bug-classes-to-review)
- [Discover repository-specific integration risks](#discover-repository-specific-integration-risks)
- [Review and fix procedure](#review-and-fix-procedure)
- [Rebase-specific rule](#rebase-specific-rule)
- [Completion gate](#completion-gate)

## Review objective

A clean textual merge is not evidence that two change sets compose correctly. Review the final integrated behavior as if debugging a regression caused by combining two independently correct branches.

The primary targets are:

- code changed by one or both original branches that did not conflict;
- callers/callees and shared state that connect the two change sets;
- conflict-resolution rewrites that alter assumptions outside marker locations;
- integration fixes added after Git-level conflict resolution.

## Build stable comparison sets

Use SHAs recorded before the operation. Do not rely on branch names that may have moved during rebase.

Construct, as applicable:

- base -> original current/source side;
- base -> original target/upstream side;
- base or target/upstream -> final integrated result;
- original replayed commits -> rebased commits when range comparison is useful.

Useful local commands include:

```bash
git diff --name-status <base>..<side-a>
git diff --name-status <base>..<side-b>
git diff <base>..<side-a> -- <path>
git diff <base>..<side-b> -- <path>
git show <commit>
git log -p -- <path>
git blame <rev> -- <path>
git range-diff <old-range> <new-range>
```

## Build an interaction map

Start from both change sets, then expand by semantics rather than merely by files:

1. Changed functions, methods, types, constants, enums, schemas, state variables, configuration, and generated interfaces.
2. Callers and callees of changed APIs.
3. Shared data structures and global/member state read or written by both sides.
4. Ownership, lifetime, cleanup, and resource relationships.
5. Producer/consumer and cache/invalidation relationships.
6. Threading, callbacks, futures, queues, events, atomics, locks, fences, and asynchronous dependencies.
7. Serialization/deserialization and cross-process/protocol dependencies.
8. Build flags, feature flags, platform conditionals, generated artifacts, and code-generation inputs.
9. Tests that specify the changed contracts.

Prioritize semantic neighborhoods touched by both branches, directly or transitively.

## Required bug classes to review

### Semantic value collisions

Look for both branches changing the meaning, default, valid range, unit, coordinate space, sentinel, enum value, or interpretation of the same logical value without touching the same lines.

Example: one branch redefines `timeout == 0` to mean "disabled" while the other adds code that still treats zero as "immediate".

### Preconditions and invariant drift

Check whether one branch changes what must be true before a function/state is used while the other adds callers that satisfy only the old contract.

Inspect nullability, initialization state, validity flags, object phase/state, thread affinity, ownership, ranges, and feature-gating assumptions.

### Postcondition and result-contract drift

Check whether callers still assume an old return value, side effect, ownership transfer, error state, synchronization point, or lifetime after another branch changes it.

### Dependency drift

Check whether one branch changes how a value/resource is produced, cached, invalidated, refreshed, or destroyed while the other adds consumers based on the prior dependency model.

### Ordering and temporal bugs

Look for operations that are individually correct but become incorrectly ordered when both branches are present: initialization/use, enqueue/flush, register/notify, update/render, acquire/release, create/destroy, write/read, or invalidate/recompute.

### Async and concurrency interactions

Review:

- stale reads and asynchronous producer/consumer mismatches;
- missing synchronization or memory visibility;
- changed lock ordering or lock coverage;
- callbacks/futures outliving owners;
- work queued with data whose lifetime/meaning changed;
- cancellation/shutdown races;
- duplicated scheduling or completion signaling.

### Ownership and lifetime bugs

Check for dangling references, double release, leaks, premature destruction, newly retained resources, invalid iterators/handles, changed RAII/cleanup responsibility, and cleanup paths that only match one branch's model.

### State-machine inconsistencies

If either branch adds/removes/renames states or transitions, verify every producer/consumer agrees on the final transition graph and invalid-state behavior.

### API contract drift that still compiles

Look for stale callers hidden by overloads, default parameters, implicit conversion, duck typing, optional fields, ABI-compatible changes, or permissive interfaces.

Compilation alone does not prove the call still means the same thing.

### Duplicated or missing side effects

Check registration, notification, invalidation, initialization, cleanup, submission, mutation, logging, metrics, scheduling, and persistence for:

- both branches independently doing the same side effect;
- one branch moving a side effect while another adds a new path that bypasses it.

### Cache and invalidation inconsistencies

Verify cache keys, generation counters, dirty flags, dependency versions, invalidation timing, memoized results, and lazy recomputation against both branches' final semantics.

### Error, retry, fallback, and cancellation drift

Check whether one side changes failure semantics while the other relies on old retryability, fallback behavior, exception/error codes, partial-result rules, or cancellation guarantees.

### Configuration and feature-flag inconsistencies

Review changed defaults, environment/config keys, feature flags, build switches, runtime capability checks, and platform-specific paths. Ensure every newly added caller/path applies the final gating semantics.

### Schema, serialization, and protocol mismatches

Verify writers/readers, versioning, defaults, optional fields, migration logic, binary layout, generated bindings, and compatibility behavior evolve together.

### Generated/source-of-truth mismatches

Check schemas, generated APIs, shaders/interfaces, reflection metadata, build manifests, lockfiles, codegen outputs, or bindings whenever one side changes source inputs and the other changes derived consumers.

### Platform and build-configuration gaps

Inspect conditional compilation and target-specific implementations. Two branches can merge cleanly in the primary configuration while leaving another platform or feature combination invalid.

### Tests that became semantically obsolete

A test may still pass while asserting an old or incomplete contract. Compare changed production behavior against tests from both sides and ensure assertions still protect the original intentions.

## Discover repository-specific integration risks

The categories above are mandatory starting points, not an exhaustive checklist. Derive additional risks from the codebase's architecture. Examples include GPU/CPU synchronization, transaction boundaries, distributed consistency, memory layout, event loops, reference counting, plugin lifecycle, database migration ordering, or incremental build state.

## Review and fix procedure

For each interaction candidate:

1. State the invariant/contract expected after integration.
2. Compare how side A and side B each change that invariant.
3. Trace the final integrated control/data flow through relevant callers and dependencies.
4. Classify the interaction as safe, suspicious, or defective.
5. For a defect, identify why neither branch alone necessarily exposed it.
6. Implement the smallest coherent integration fix, even in a non-conflicted file.
7. Add/adapt focused tests when they can distinguish the combined behavior.
8. Stage the fix and re-review the affected semantic neighborhood.
9. Record the finding, resolution, files, and verification for reporting.

Do not perform broad unrelated refactors during this review.

## Rebase-specific rule

A completed rebase may already contain rewritten commits. If this review finds additional bugs after rebase completion, fix and stage them but do not automatically amend, reset, or rewrite the rebased commits. Those history changes require explicit user permission.

## Completion gate

The integration code review passes only when:

- every high-risk interaction between the two original change sets has been examined to a defensible boundary;
- discovered integration defects are fixed and focused-tested;
- no unresolved semantic/product/architecture decision remains;
- the affected-test scope has been updated to include review fixes.

Only then proceed to final impact-based verification.
