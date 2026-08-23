# Static Performance Review Checklist

Use when code cannot be run locally or when reviewing a diff before benchmarking. Mark every finding as a **hypothesis until measured**.

Load detail references when a section applies:

- source smells and fixes: [cpp-language-patterns.md](cpp-language-patterns.md)
- layout, allocations, false sharing: [memory-layout-and-allocations.md](memory-layout-and-allocations.md)
- threads, atomics, NUMA: [parallelism-and-contention.md](parallelism-and-contention.md)
- build flags and codegen: [compiler-build-and-remarks.md](compiler-build-and-remarks.md)

## Hot path classification

- What runs per frame, request, item, tick, or in tight loops?
- What runs once at startup or rarely?
- Is the target latency, throughput, memory, frame time, binary size, or compile time?
- Are there explicit budgets or regression thresholds?

## Algorithm and work done

Ask: can work be removed, hoisted, batched, cached with clear invalidation, or made incremental?

Check for nested loops, repeated sorting/parsing/querying, unnecessary intermediate containers, duplicate cross-layer work. See [cpp-language-patterns.md](cpp-language-patterns.md#algorithms-and-recomputation).

## Allocation and copies

Check hot paths for growth without `reserve`, temporaries, `std::function`/`shared_ptr`, regex, iostreams, or formatting per item, large pass-by-value, `return std::move(local)`. Permit clarity-oriented copies outside hot paths for small trivial values. See [memory-layout-and-allocations.md](memory-layout-and-allocations.md#allocation-churn) and [cpp-language-patterns.md](cpp-language-patterns.md#ownership-and-type-erasure).

## Containers and layout

Check for `std::map` without ordering need, list/pointer-graph traversal, polymorphic object vectors, mixed hot/cold fields, `std::vector<bool>`, string-key lookups that allocate. See [memory-layout-and-allocations.md](memory-layout-and-allocations.md#containers) and [cpp-language-patterns.md](cpp-language-patterns.md#containers-and-lookups).

## Dispatch and abstraction

Check for virtual calls, `dynamic_cast`, or `std::function` inside tiny inner loops; callbacks invoked per item when dispatch could move outside the loop. Do not remove abstraction unless measured cost matters. See [cpp-language-patterns.md](cpp-language-patterns.md#virtual-dispatch-and-inlining).

## Concurrency

Check for global locks, per-item atomics, shared counters, expensive work under lock, condition-variable waits without predicates, false-sharing-prone adjacent fields, unbounded queues. Require tests and race validation for lock-free or relaxed-memory changes. See [parallelism-and-contention.md](parallelism-and-contention.md) and [memory-layout-and-allocations.md](memory-layout-and-allocations.md#false-sharing).

## I/O and logging

Check for logging in hot loops, `std::endl` flushing, per-item open/close or DB calls, repeated parsing. See [cpp-language-patterns.md](cpp-language-patterns.md#io-and-syscalls).

## Build and codegen

Check for unoptimized benchmark builds, missing debug symbols, unmeasured LTO/PGO claims, obvious missed vectorization, branch hints without branch-miss evidence, cargo-cult `inline`/`[[likely]]`. See [compiler-build-and-remarks.md](compiler-build-and-remarks.md) and [cpp-language-patterns.md](cpp-language-patterns.md#branch-prediction).

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
