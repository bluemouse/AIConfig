---
name: cpp-performance-guide
description: "Comprehensive C++ performance optimization and investigation guidance. Use when profiling, benchmarking, reviewing, or improving C/C++ runtime performance, latency, throughput, memory use, allocations, cache locality, branch behavior, compiler optimization, vectorization, concurrency, lock contention, NUMA scaling, binary size, startup time, compile time, or regressions — even if the user says 'make it faster' without naming a profiler. Use for native desktop apps, services, libraries, game engines, rendering systems, finance/scientific workloads, Qt apps, mobile native stacks, and performance sign-off requiring reproducible measurements, tests, and a compact report."
---

# C++ Performance Guide

Resolve `<SKILL_ROOT>` as the directory containing **this** skill's `SKILL.md`. Resolve paths to `references/` and `scripts/` from that directory.

Optimize by evidence, not intuition. Preserve correctness first, then improve the bottleneck that measurements identify.

For general C++20 style, see [`../cpp-coding/SKILL.md`](../cpp-coding/SKILL.md). For allocation and ownership design, see [`../cpp-memory-guide/SKILL.md`](../cpp-memory-guide/SKILL.md). For regression tests and Google Benchmark targets, see [`../cpp-testing/SKILL.md`](../cpp-testing/SKILL.md). For root-cause diagnosis before optimizing, see [`../debugging-guide/SKILL.md`](../debugging-guide/SKILL.md).

## When to Use

- Profiling, benchmarking, or triaging C/C++ runtime performance regressions
- Investigating latency, throughput, cache misses, allocations, contention, or scaling
- Reviewing hot paths for measured or hypothesized bottlenecks
- Tuning build flags, codegen, vectorization, or parallelization with before/after evidence

## When NOT to Use

- Non-C++ code — use a language-specific skill
- Web-only performance (Core Web Vitals, frontend bundle size) — out of scope
- Active defect triage without a performance target — use **debugging-guide** first
- Memory leak or ownership design without a performance focus — use **cpp-memory-guide**
- Adding or fixing tests without a performance investigation — use **cpp-testing**

## Completion rule

Do not present performance work as complete unless you can show:

1. target metric and representative workload,
2. release-like build configuration,
3. baseline measurement,
4. bottleneck evidence,
5. correctness validation,
6. isolated change or clearly labeled recommendation,
7. before/after result with variance or confidence notes, and
8. tradeoffs, risks, and next step.

If benchmarks or profilers cannot run in the environment, state that plainly and provide exact commands for the user to run. Label unmeasured recommendations as hypotheses.

## Default workflow

1. **Set the target**
   - Identify the primary metric: wall time, p50/p95/p99 latency, throughput, frame time, CPU time, peak RSS, allocations/op, cache misses, binary size, compile time, or scaling efficiency.
   - Identify workload, input size, platform, compiler, build type, hardware, thread count, and acceptance threshold.
   - If the user did not provide a workload, infer a reasonable local workload and state the assumption.

2. **Build the right binary**
   - Prefer `RelWithDebInfo` or `Release` with debug symbols.
   - Keep optimization and profiling flags reproducible in the build system, not only in an ad hoc shell command.
   - For Linux `perf` call graphs, add frame pointers when using frame-pointer unwinding: `-fno-omit-frame-pointer`.
   - Never benchmark `Debug` or sanitizer builds as final performance evidence.

3. **Check available tools**
   - Run `scripts/check-tools.sh` first when a shell is available.
   - Use native tools by platform; see [tool-recipes.md](references/tool-recipes.md).
   - If Linux PMU counters are unavailable in a VM/container, use wall-clock benchmark repetition, Callgrind/Cachegrind, heap profilers, or native host tools.

4. **Establish a baseline**
   - Prefer an end-to-end benchmark for user-visible performance.
   - Use microbenchmarks only for isolated kernels, container choices, allocator behavior, algorithm variants, and codegen questions.
   - Use warmup, repetitions, stable inputs, stable build flags, and captured environment details.
   - For Google Benchmark JSON, run `scripts/run-google-benchmark.sh <bench-binary>` and compare JSON outputs with `scripts/compare_benchmark_json.py`.
   - See [measurement-and-benchmarking.md](references/measurement-and-benchmarking.md).

5. **Find the real bottleneck**
   - First classify the workload. On Intel Linux, try `perf stat -M TopdownL1 -- ./binary`; on AMD Zen 4+, try `perf stat -M PipelineL1 -- ./binary`.
   - If top-down metrics are unavailable, collect cycles, instructions, branches, branch misses, cache misses, page faults, context switches, and elapsed time.
   - Use flamegraphs or profiler timelines to locate hotspots before editing.
   - For long-running or frame-based programs, consider Tracy zones and native timeline profilers.

6. **Load only the relevant reference**
   - CPU hotspot or benchmark setup: [measurement-and-benchmarking.md](references/measurement-and-benchmarking.md), [tool-recipes.md](references/tool-recipes.md)
   - Missed inlining/vectorization/codegen or build tuning: [compiler-build-and-remarks.md](references/compiler-build-and-remarks.md)
   - Memory, cache, allocations, false sharing: [memory-layout-and-allocations.md](references/memory-layout-and-allocations.md)
   - Poor scaling, contention, atomics, NUMA, parallelism: [parallelism-and-contention.md](references/parallelism-and-contention.md)
   - Source-level performance review: [cpp-language-patterns.md](references/cpp-language-patterns.md), [review-checklist.md](references/review-checklist.md)

7. **Choose the least invasive fix in this order**
   1. remove unnecessary work
   2. improve algorithmic complexity
   3. reduce recomputation and call frequency
   4. improve data layout and locality
   5. reduce allocations, copies, ownership churn, and type erasure
   6. batch I/O and synchronization
   7. reduce contention, false sharing, and NUMA traffic
   8. simplify code so the compiler can optimize it
   9. add vectorization, compiler-specific specialization, PGO/LTO/BOLT, or SIMD only after evidence

8. **Implement narrowly**
   - Change one high-confidence thing per measurement loop whenever practical.
   - Prefer removing work over hiding work.
   - Do not introduce global caches, object pools, lock-free structures, relaxed math, or new concurrency models without proof and explicit risk notes.
   - Keep public API, ordering, numerical behavior, lifetime rules, and thread-safety unless the user approves a semantic change.

9. **Validate correctness and performance**
   - Run unit/integration/regression tests after changes.
   - Run sanitizers or race-checking tools when ownership, indexing, lifetime, atomics, or concurrency changed.
   - Re-run the same benchmark/profile after each material change.
   - If parallelized, measure the 1-thread baseline and a scaling curve, not only the best thread count.

10. **Report**
   - Finish with the compact template in [performance-report.md](references/performance-report.md).
   - Include exact commands, numbers, deltas, changed files, tests, and residual risks.

## Rules that override instincts

- Do not claim a speedup without measurement.
- Do not optimize cold code unless it affects startup, memory footprint, binary size, or user-visible latency.
- Do not default to `-Ofast`; treat relaxed math as a semantic change.
- Do not assume more threads means faster; prove the code is not bandwidth-bound, synchronization-bound, or NUMA-bound.
- Do not trust a microbenchmark until setup cost, data size, cache state, warmup, and compiler-elimination risks are controlled.
- Do not use sanitizer timings as final performance numbers.
- Do not replace readable code with clever code unless the measured gain matters.

## Common hotspot playbook

- `malloc`, `operator new`, allocator locks in top frames: reserve/reuse storage, use views, hoist allocation, use arenas or `std::pmr`, or test allocator alternatives.
- Cache misses or wide basic loops with low useful work: shrink working set, improve data layout, split hot/cold fields, use contiguous storage, consider SoA.
- Branch misses: sort/group data, simplify conditions, remove unpredictable branches, use hints only after proof.
- `std::map`, `std::list`, pointer-rich graphs in hot paths: consider flat/contiguous/hash structures.
- Repeated sort/parse/query/recompute in loops: precompute, cache with clear invalidation, incrementally update, or batch.
- `std::function`, virtual dispatch, `dynamic_cast`, `shared_ptr` churn in hot loops: use concrete types, templates, `function_ref`, variants, ownership simplification, or devirtualization.
- Mutexes, atomics, shared counters: shard, use thread-local accumulation plus reduce, minimize critical sections, batch writes, and check false sharing.
- I/O/logging/database per item: batch, buffer, stream once, hold handles, async only when it simplifies the measured bottleneck.

## Bundled scripts

Execute scripts with `bash`; do not inline their contents.

| Script | Use |
|---|---|
| `scripts/check-tools.sh` | show available profilers, benchmark tools, CPU, governor, and perf permissions |
| `scripts/run-perf-stat.sh <binary> [args]` | repeated Linux counter triage; env: `PERF_REPEAT`, `PERF_EVENTS`, `CPUSET`, `NUMA_NODE` |
| `scripts/run-perf-record.sh <binary> [args]` | Linux sampling profile and optional FlameGraph SVG; env: `PERF_FREQ`, `PERF_CALLGRAPH`, `FLAMEGRAPH_DIR`, `CPUSET`, `NUMA_NODE` |
| `scripts/run-google-benchmark.sh <bench-binary> [args]` | Google Benchmark JSON run with repetitions and warmup; env: `BENCH_REPS`, `BENCH_WARMUP`, `BENCH_FILTER`, `BENCH_OUT` |
| `scripts/collect-compiler-remarks.sh <clang|gcc> <out-dir> -- <compile-cmd>` | collect optimization/vectorization remarks for one compile command |
| `scripts/compare_benchmark_json.py before.json after.json` | compare Google Benchmark JSON or simple metric JSON files; prefer `*_mean` aggregate rows when using repetitions (see [measurement-and-benchmarking.md](references/measurement-and-benchmarking.md)) |

## References

- [measurement-and-benchmarking.md](references/measurement-and-benchmarking.md): benchmark hygiene, perf counters, top-down triage, Google Benchmark, noise control.
- [tool-recipes.md](references/tool-recipes.md): copy-paste profiler recipes for Linux, macOS/iOS, Windows, Android, Qt, game/rendering, and non-PMU environments.
- [compiler-build-and-remarks.md](references/compiler-build-and-remarks.md): CMake build modes, frame pointers, optimization remarks, assembly inspection, PGO, LTO, BOLT.
- [memory-layout-and-allocations.md](references/memory-layout-and-allocations.md): locality, SoA/AoS, `std::pmr`, allocator alternatives, false sharing, cache behavior.
- [parallelism-and-contention.md](references/parallelism-and-contention.md): OpenMP, oneTBB, `std::execution`, atomics, locks, NUMA, race validation.
- [cpp-language-patterns.md](references/cpp-language-patterns.md): C++ source-level patterns and anti-patterns.
- [review-checklist.md](references/review-checklist.md): static review rubric when code cannot be run.
- [performance-report.md](references/performance-report.md): final report template.
