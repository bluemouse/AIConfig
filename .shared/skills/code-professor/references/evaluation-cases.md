# Evaluation cases

Use fresh agent sessions and real or representative repositories. Judge evidence quality, cleanup, usefulness, and restraint rather than document length.

## Evaluation 1: Broad onboarding

Prompt:

`Use code-professor to teach me this repository. I am a developer joining the project and need a reading path.`

Expected behavior:

- selects repository orientation guide
- reads repository instructions first
- identifies build, test, entry points, major boundaries, and reading order
- cites substantive claims with stable path:line references
- does not edit code
- distinguishes verified commands from inferred commands

## Evaluation 2: Focused module

Prompt:

`Use code-professor to explain the caching module, especially ownership, invalidation, concurrency, and how to extend it.`

Expected behavior:

- selects module deep dive
- traces callers and downstream consumers, not only files inside the module
- explains invariants and concurrency with evidence
- maps tests to behavior
- separates current behavior from extension suggestions

## Evaluation 3: Workflow trace

Prompt:

`Use code-professor to trace a request from the public API to the final database write, including validation and error paths.`

Expected behavior:

- selects workflow trace
- follows every synchronous and asynchronous boundary
- explains data transformations and configuration branches
- cites every substantive stage
- includes failure and cleanup paths

## Evaluation 4: Runtime investigation

Prompt:

`Use code-professor to investigate why this operation intermittently returns stale data. You may build, test, and add temporary diagnostics.`

Expected behavior:

- records repository baseline
- starts with static evidence and focused tests
- instruments only if necessary
- snapshots every edited path before modification
- marks and removes temporary code
- verifies exact restoration and preserves pre-existing changes
- provides either a supported root cause or ranked hypotheses
- does not apply a permanent fix unless explicitly requested

## Evaluation 5: Explicit fix request (handoff)

Prompt:

`Use code-professor to investigate and fix this crash, then explain the root cause and validation.`

Expected behavior:

- recognizes verified repair is primary — defer to debugging-guide, or complete a failure investigation guide first then hand off for the fix
- does **not** apply a production patch as the code-professor terminal outcome
- if producing an investigation guide first, ends with a clear handoff to debugging-guide for implement-and-verify

## Evaluation 6: Near-miss boundaries

Prompt:

`Review my staged diff for security issues.`

Expected behavior:

- does **not** use code-professor as primary workflow
- defers to code-reviewer

Prompt:

`Fix this segfault and verify with tests.`

Expected behavior:

- defers to debugging-guide unless user explicitly wants investigation documentation first
