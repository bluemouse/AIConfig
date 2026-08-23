# Parallelism and Contention

## Table of contents
- Before adding threads
- Choosing a parallel model
- `std::execution`
- OpenMP
- oneTBB
- Contention reduction
- Atomics and memory ordering
- NUMA
- Correctness validation

## Before adding threads

Add parallelism only after measurement shows useful parallel work exists. Check:

- Is the code already memory-bandwidth-bound?
- Is the workload large enough to amortize scheduling overhead?
- Can work be partitioned with minimal shared writes?
- Does result ordering matter?
- Are floating-point reductions allowed to change association/order?
- Does the project already use a concurrency runtime?

Measure a 1-thread baseline and a scaling curve: 1, 2, 4, 8, ... threads up to the target machine.

## Choosing a parallel model

Prefer the existing project model unless evidence supports a change.

- `std::execution`: concise data-parallel algorithms where library support is real.
- OpenMP: regular loop nests, reductions, quick experiments, numerical kernels.
- oneTBB: task decomposition, blocked ranges, pipelines, work stealing, nested parallelism.
- custom thread pools: use when the project already owns scheduling requirements.

Avoid introducing a new runtime for a small localized gain unless the maintainers accept the dependency and scheduling implications.

## `std::execution`

Policies:

- `std::execution::seq`: sequential.
- `std::execution::par`: parallel execution permitted.
- `std::execution::unseq`: vectorized/unsequenced execution permitted.
- `std::execution::par_unseq`: parallel and vectorized/unsequenced permitted.

Cautions:

- Some standard libraries run `par` serially without an enabled backend.
- `par_unseq` / `unseq` bodies must not rely on inter-iteration ordering or use synchronization that is not allowed for unsequenced execution.
- Test the actual implementation; do not assume parallelism because the policy is present.

## OpenMP

Useful for regular loops:

```cpp
#pragma omp parallel for schedule(static) reduction(+:sum)
for (std::size_t i = 0; i < n; ++i) {
    sum += work(i);
}
```

Rules:

- use reductions instead of shared atomics when possible,
- choose `schedule(static)` for predictable equal work,
- test `dynamic` or `guided` only when imbalance is measured,
- keep loop bodies free of hidden locks/allocation where possible,
- document required compiler flags and runtime dependencies.

## oneTBB

Useful for blocked ranges and task graphs:

```cpp
tbb::parallel_for(tbb::blocked_range<std::size_t>(0, n),
  [&](const tbb::blocked_range<std::size_t>& r) {
    for (std::size_t i = r.begin(); i != r.end(); ++i) {
      work(i);
    }
  });
```

Use `parallel_reduce` for reductions and avoid global mutable state in task bodies.

## Contention reduction

Symptoms:

- time in mutex/condition variable calls,
- high context switches,
- high atomics cost,
- poor scaling despite available CPU,
- `perf c2c` showing cache line bouncing.

Fixes:

- reduce critical section size,
- snapshot shared data under lock then compute outside,
- shard by key/thread/core,
- use thread-local accumulation and reduce,
- batch queue pushes and logging,
- replace shared counters with per-thread counters,
- separate hot mutable fields into different cache lines.

## Atomics and memory ordering

Atomics are not free. In tight loops, even relaxed atomics can serialize or bounce cache lines.

Guidance:

- avoid per-item atomic updates when per-thread reduction works,
- use the weakest correct ordering, but only with a written invariant,
- prefer `memory_order_relaxed` only for independent counters/statistics,
- do not guess at lock-free correctness; add stress tests and race tools.

## NUMA

NUMA can dominate large memory workloads. Measure before optimizing:

```bash
numactl --hardware
numactl --cpunodebind=0 --membind=0 ./binary
```

Fixes:

- first-touch initialization on the worker that will use the memory,
- partition data by NUMA node,
- avoid cross-node queues in hot paths,
- pin worker pools only when the runtime and deployment permit it.

## Correctness validation

Parallel performance changes need stronger validation:

- unit and integration tests,
- ThreadSanitizer when feasible,
- deterministic/reproducibility tests when ordering matters,
- stress tests with many seeds and thread counts,
- numerical tolerance review for floating-point reductions.

Never call a parallel speedup complete without correctness evidence.
