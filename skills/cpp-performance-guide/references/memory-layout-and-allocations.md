# Memory Layout and Allocations

## Table of contents
- Locality principles
- Containers
- Copies and views
- Allocation churn
- `std::pmr`
- False sharing
- Cache and NUMA symptoms
- Memory anti-patterns

## Locality principles

Memory is often the bottleneck even when CPU samples point at ordinary loops. Prefer:

- contiguous storage over pointer graphs,
- smaller hot structs,
- hot/cold field splitting,
- predictable access order,
- batching to amortize fixed costs,
- direct indexing over repeated associative lookups when lifecycle allows it.

Do not optimize layout blindly. Confirm with profiling, counters, or clear hot-path reasoning.

## Containers

Performance-oriented defaults:

- `std::vector`: best default for contiguous, append/iterate-heavy hot paths.
- `std::deque`: stable references and segmented storage, weaker locality than vector.
- `std::unordered_map`: average O(1), but node-based implementations allocate per insert and have pointer chasing.
- flat hash maps (`absl::flat_hash_map`, `boost::unordered_flat_map`, `ankerl::unordered_dense::map`): often better locality for hot hash tables.
- `std::map`: ordered tree; avoid in hot lookup paths unless ordering or iterator stability is required.
- `std::list` / `std::forward_list`: usually poor for performance due to allocation and cache misses.

Use `reserve()` for vectors and hash maps when size is known.

## Copies and views

Use views when ownership is not required:

- `std::span<T>` / `std::span<const T>` for arrays and vectors,
- `std::string_view` for read-only string data with clear lifetime,
- `const T&` for large read-only objects,
- pass-by-value for small trivial objects or sink parameters you will move into storage.

Avoid `return std::move(local)`; it can disable guaranteed copy elision or NRVO.

## Allocation churn

Symptoms:

- `malloc`, `free`, `operator new`, allocator locks, or reference counting high in the profile,
- many temporary strings/vectors/maps in loops,
- container growth without reserve,
- `std::function`, `std::shared_ptr`, regex, streams, or formatting in tight paths.

Fixes:

- hoist allocation out of loops,
- reserve and reuse buffers,
- batch per-item objects,
- use small object/value storage when practical,
- use `std::string_view`/`std::span` for read-only paths,
- avoid repeated string concatenation with `+`; use `reserve()` plus `append()` or `format_to` into a buffer,
- test allocator alternatives only after proving allocator cost matters.

## `std::pmr`

Use `std::pmr` for phase-oriented allocation or many short-lived objects.

- `std::pmr::monotonic_buffer_resource`: fast bump allocation, releases all at once, not thread-safe.
- `std::pmr::unsynchronized_pool_resource`: single-thread pool allocation.
- `std::pmr::synchronized_pool_resource`: shared multi-thread pool allocation.

Always define ownership, lifetime, memory cap, and reset point. Do not hide unbounded growth inside an arena.

## False sharing

False sharing happens when threads mutate different variables on the same cache line. Symptoms include poor scaling and high coherence traffic despite little logical sharing.

Fixes:

- pad or align per-thread mutable state,
- use arrays of per-thread counters and reduce later,
- separate read-mostly from frequently mutated fields,
- avoid adjacent atomics updated by different threads.

`std::hardware_destructive_interference_size` can be useful but is not always ABI-stable in public headers. Hard-code internally with platform notes when necessary.

## Cache and NUMA symptoms

Memory-bound signs:

- high Backend Bound -> Memory in top-down metrics,
- high cache miss rate,
- low IPC with many stalled cycles,
- speedup plateaus as threads increase,
- remote NUMA access on multisocket machines.

Investigate with:

```bash
perf stat -e cache-references,cache-misses,cycles,instructions -- ./binary
perf mem record -- ./binary
perf c2c record -- ./binary
numactl --hardware
```

When NUMA matters, measure with fixed CPU and memory placement before changing code.

## Memory anti-patterns

Flag these in hot paths:

- `std::vector<bool>` proxy behavior,
- `std::list` for frequent traversal,
- polymorphic object vectors with scattered allocation,
- JSON/string parsing per item,
- repeated `std::string` construction for map lookups,
- `std::shared_ptr` where `std::unique_ptr`, value, or reference would do,
- unbounded caches without invalidation.
