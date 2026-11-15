# Impact-based testing and verification

Use this stage after integration code review. Its purpose is to demonstrate that all locally discoverable tests directly or indirectly affected by either branch and by integration fixes pass in the final integrated tree.

## Contents

- [Hard success rule](#hard-success-rule)
- [Build the affected-test set](#build-the-affected-test-set)
- [Use local dependency information](#use-local-dependency-information)
- [Expand scope conservatively](#expand-scope-conservatively)
- [Required non-test checks](#required-non-test-checks)
- [Interpret failures as evidence](#interpret-failures-as-evidence)
- [Failure/fix loop](#failurefix-loop)
- [Flaky and nondeterministic tests](#flaky-and-nondeterministic-tests)
- [Skipped or unavailable tests](#skipped-or-unavailable-tests)
- [Completion record](#completion-record)

## Hard success rule

Do not declare `VERIFIED SUCCESS` until every required affected test passes.

A required affected test that fails, is skipped, cannot run, or is blocked means `NOT VERIFIED`. Git operation completion, compilation, or a partially green test run is not a substitute.

## Build the affected-test set

Start from three change sources:

1. original side A changes from the recorded merge base;
2. original side B/target/upstream changes from the recorded merge base;
3. all conflict resolutions and additional integration-review fixes.

Discover tests using repository-local evidence.

### Directly affected tests

Include:

- tests modified by either branch;
- tests added for commits being integrated;
- tests corresponding directly to changed source files, modules, classes, APIs, shaders, schemas, or components;
- regression tests associated with locally visible bug-fix commits.

### Indirectly affected tests

Expand through plausible behavioral dependencies, including:

- callers of changed APIs and tests of those callers;
- consumers of changed types, state, configuration, or schemas;
- downstream build/test targets that link or depend on changed targets;
- component/subsystem suites containing changed code;
- integration tests crossing components changed by different branches;
- tests that exercise shared state, caches, invalidation, ownership, lifetime, cleanup, or resource management touched by either side;
- concurrency/async tests when threads, tasks, queues, callbacks, atomics, locks, synchronization, ordering, or lifetime changed;
- serialization/compatibility/migration tests when data contracts changed;
- platform/configuration/feature-flag variants when conditional code or defaults changed;
- generated-code consistency tests when source-of-truth or generated interfaces changed;
- tests protecting invariants discovered during integration code review.

## Use local dependency information

Prefer authoritative local relationships when available:

- build-system target/dependency graphs;
- test manifests and suite definitions;
- package/module dependency metadata;
- source call/reference search;
- project files and generated dependency lists;
- CI configuration as documentation of local commands and test groupings;
- repository scripts, Makefiles, task runners, and developer docs.

Do not contact remote CI, download dependencies, or fetch external history under this skill.

## Expand scope conservatively

Use this escalation ladder:

1. direct unit/regression tests;
2. dependent target/component tests;
3. cross-component integration tests;
4. broader subsystem suites;
5. platform/configuration variants affected by the changes;
6. full local test suite when the impact boundary cannot be established confidently.

Do not stop at a narrow test set simply because it passes. The chosen boundary must account for both branch change sets and all integration fixes.

## Required non-test checks

Run applicable local checks for affected areas, including:

- compilation/build;
- type checking;
- static analysis;
- lint;
- formatting/check-format;
- code-generation consistency;
- schema/protocol validation;
- packaging/linking or target-generation checks;
- repository-specific correctness tools.

Use commands already supported by the local repository/toolchain. Do not install/fetch network dependencies automatically.

## Interpret failures as evidence

For each failure, determine whether it indicates:

- a conflict-resolution bug;
- a clean-merge semantic interaction bug;
- a wrong integration-review assumption;
- an affected build/configuration dependency that was missed;
- an environment/tooling limitation;
- an unrelated/pre-existing failure.

Do not weaken assertions, delete tests, disable checks, or add broad suppressions merely to get green output.

Even if a failure appears pre-existing, the final integration cannot be marked `VERIFIED SUCCESS` while a required affected test still fails. Explain the evidence and leave the result `NOT VERIFIED` unless the final affected test set passes.

When a required affected test was already failing before the integration began, report that distinction explicitly:

- **Integration-introduced failure** — new or changed behavior from combining the branches or from integration fixes; must be fixed before `VERIFIED SUCCESS`.
- **Pre-existing baseline failure** — the same test/suite was already failing on the pre-integration branch tip or merge base; the integration still cannot be `VERIFIED SUCCESS`, but note that the failure may not be caused by this merge/rebase.
- **Inconclusive** — insufficient local evidence to tell; treat as blocking and describe what comparison would resolve it (for example, run the test on each recorded pre-operation SHA).

Do not claim the integration is verified while required affected tests remain red, regardless of cause.

## Failure/fix loop

When a test reveals an integration defect:

1. reproduce/understand the failure locally;
2. trace it to the interaction between branch changes or integration fixes;
3. implement the coherent code/test fix;
4. perform a focused integration code review around the fix;
5. update the affected-test graph if new dependencies changed;
6. rerun the failing test;
7. rerun every affected suite whose assumptions may have changed;
8. continue until all required affected tests pass.

## Flaky and nondeterministic tests

Do not treat one eventual pass as proof when the integration may have introduced timing/concurrency instability. Investigate repeatability and relevant synchronization/lifetime changes. If confidence cannot be established, mark verification `NOT VERIFIED` and report the residual risk.

## Skipped or unavailable tests

A required affected test may be unavailable because of missing local dependencies, hardware, platform, permissions, services, or tooling. Do not fetch/install remotely under this skill. Record:

- the exact test/suite;
- why it is affected;
- why it could not run;
- what environment is needed;
- what remains unverified.

The overall result remains `NOT VERIFIED` until required affected tests pass.

## Completion record

Before final structural validation, record:

- affected-test discovery method;
- direct tests run and results;
- dependent/component tests run and results;
- integration/subsystem tests run and results;
- platform/configuration variants run and results;
- full suite result if run;
- applicable build/static/lint/format/codegen checks;
- failures encountered and integration fixes they caused;
- required tests that are skipped/blocked/unavailable.

Proceed as `VERIFIED SUCCESS` only when required affected tests and checks are all green.
