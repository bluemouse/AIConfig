# Diagnostic Techniques

Use these techniques selectively when the main workflow needs more precision.

## Minimal reproduction

- Reduce the failing scenario until only one behavior remains.
- Preserve the same observable failure while removing unrelated setup.
- Prefer a unit test for local logic, an integration test for boundary bugs, and a script when no harness exists.
- Record the smallest input, seed, config, platform, and environment that still fails.

## Backward tracing

Start from the bad observation and walk backward:

1. Where is the bad value, state, timing, output, or error first observed?
2. Which caller or producer supplied it?
3. Where was it parsed, converted, cached, owned, mutated, scheduled, generated, or fetched?
4. What invariant should have rejected or transformed it earlier?
5. What change allowed the invariant to break?

Stop at the earliest incorrect transition. Fix there.

## Boundary instrumentation

For multi-step flows, inspect each boundary before changing code:

- input and output values;
- identity, type, size, ownership, lifetime, nullability, encoding, and units;
- config, environment variables, flags, permissions, locale, timezone, and paths;
- thread, process, transaction, request id, frame id, event id, or coroutine/task id;
- ordering, timing, retries, debounce/throttle state, cache state, and external-service responses.

**Tripwire discipline:** add instrumentation only when it surfaces the fault earlier or where
it is cheaper to act on — not to restate what the crash or debugger already showed. See
`instrumentation-and-checks.md`.

Remove temporary diagnostics before completion unless they become intentional, low-noise observability.

## Differential comparison

Compare broken and working cases:

- same code path with different input;
- same input on different platform, build type, device, compiler, SDK, dependency, or runtime version;
- current branch against previous known-good commit;
- local environment against CI or production;
- failing test order against isolated test execution;
- similar feature that already works in the codebase.

List differences first. Do not dismiss small differences without checking them.

## Search and slicing

Use code search to find:

- all writers of the bad state;
- all readers that assume an invariant;
- all conversions, adapters, serializers, generated files, caches, and thread hops;
- all tests covering nearby behavior;
- similar previous fixes.

Use a debugger, tracepoint, temporary assertion, or focused log to narrow the dynamic slice when static reading is ambiguous.

## Binary search

Use binary search when the failing space is large:

- `git bisect` for regressions — only on deterministic repros; force clean rebuilds when results look inconsistent; see `reproduction-and-bisection.md`;
- halve feature flags, config inputs, data sets, repro steps, or scene graphs;
- split a call chain with assertions at midpoint boundaries;
- run test order or seed bisection for flakes.

## Intermittent failures

When the bug is flaky:

1. estimate frequency and capture at least one failing trace with seed, order, and environment;
2. remove nondeterminism (time, random, threading, unordered iteration, external services);
3. stress the suspect path to raise hit rate;
4. use a circular log dumped on detection or record/replay when live debugging fails;
5. treat vanishing-under-instrumentation as race evidence, not a fix.

See `determinism-and-replay.md`.

## Common bug classes

| Bug class | Evidence to seek | Fix shape |
| --- | --- | --- |
| Logic/edge case | failing assertion, truth table, missing branch, boundary input | correct condition or algorithm; add edge-case test |
| State mutation | first invalid write, ownership/lifetime transition, mutation order | move fix to writer; preserve invariant |
| Memory safety | sanitizer output, invalid lifetime, bounds, aliasing, use-after-free | correct ownership/lifetime/bounds; add sanitizer-backed test when possible |
| Concurrency | interleaving trace, lock/order invariant, race detector, thread ids | enforce synchronization/order; avoid sleeps |
| Build/config | exact command, generated files, flags, env, dependency versions | fix config propagation or generated source, not consumer workaround |
| Platform behavior | OS/API difference, path, permissions, endian, locale, timezone, SDK | isolate platform contract and test affected platform |
| Performance | profile, allocation count, hot path, input size, algorithmic complexity | fix hot path with benchmark or regression guard |
| Flakiness | repetition count, seed, time dependency, ordering, external dependency | make synchronization/data deterministic; repeat verification |
| Integration/schema | request/response payloads, schema mismatch, version skew, auth context | fix boundary contract and add contract/integration test |

## Fix selection checklist

Choose the fix that:

- changes the earliest incorrect transition;
- preserves valid existing behavior;
- is covered by a targeted regression test;
- matches local architecture and code style;
- removes ambiguity instead of hiding it;
- avoids broad catches, sleeps, global mutable state, duplicated logic, and unrelated refactoring.
