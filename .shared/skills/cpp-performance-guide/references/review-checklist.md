# Static Performance Review Checklist

Use this when code cannot be run locally or when reviewing a diff before benchmarking. Mark findings as hypotheses until measured.

## Hot path classification

- What code runs per frame, per request, per item, per bar, per tick, or in tight loops?
- What code runs once at startup or rarely?
- Are the performance requirements latency, throughput, memory, frame time, or compile time?
- Are there explicit budgets or regression thresholds?

## Algorithm and work done

Flag:

- nested loops over large inputs,
- repeated sorting/parsing/querying/recomputing,
- unnecessary materialization of intermediate containers,
- duplicate work across layers,
- missed incremental update opportunities.

Ask: can the work be removed, hoisted, batched, cached with clear invalidation, or made incremental?

## Allocation and copies

Flag in hot paths:

- container growth without reserve,
- temporary strings/vectors/maps,
- `std::function`, `std::shared_ptr`, regex, iostreams, or formatting per item,
- pass-by-value of large objects when not used as a sink,
- `return std::move(local)`.

Permit clarity-oriented copies outside hot paths, especially for small trivial values.

## Containers and layout

Flag:

- `std::map` when ordering is not used,
- `std::list`/pointer graphs during traversal,
- vector of polymorphic heap objects,
- hot structs mixing hot and cold fields,
- `std::vector<bool>`,
- string-key lookups that allocate temporaries.

## Dispatch and abstraction

Flag:

- virtual calls inside tiny inner loops,
- `dynamic_cast` in hot paths,
- `std::function` where a concrete callable or template would work,
- callbacks invoked per item when dispatch could move outside the loop.

Do not remove abstraction unless the measured cost matters.

## Concurrency

Flag:

- global locks,
- atomics per item,
- shared counters,
- lock around expensive computation,
- condition variable waits without predicates,
- false sharing risk in adjacent per-thread fields,
- unbounded queues.

Require tests and race validation for lock-free or relaxed-memory changes.

## I/O and logging

Flag:

- printing/logging in hot loops,
- flushing with `std::endl`,
- open/close per item,
- database or filesystem call per item,
- JSON/text parsing in repeated paths.

## Build and codegen

Flag:

- benchmark built without optimization,
- missing symbols for profiling,
- LTO/PGO claims without measurement,
- missed vectorization in obvious kernels,
- branch hints without branch evidence,
- `inline`/`always_inline` used as cargo cult.

## Review output

Use this compact form:

```text
Finding:
Evidence in code:
Why it may matter:
Suggested measurement:
Suggested fix:
Risk / tradeoff:
Status: hypothesis until measured
```
