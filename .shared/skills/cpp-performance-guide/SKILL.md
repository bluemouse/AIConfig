---
name: cpp-performance-guide
description: "Comprehensive C++ performance optimization and investigation guidance. Use when profiling, benchmarking, reviewing, or improving C/C++ runtime performance, latency, throughput, memory use, allocations, cache locality, branch behavior, compiler optimization, vectorization, concurrency, lock contention, NUMA scaling, binary size, startup time, compile time, or regressions — even if the user says 'make it faster' without naming a profiler. Use for native desktop apps, services, libraries, game engines, rendering systems, finance/scientific workloads, Qt apps, mobile native stacks, and performance sign-off requiring reproducible measurements, tests, and a compact report."
---

# C++ Performance Guide

Resolve `<SKILL_ROOT>` as the directory containing **this** skill's `SKILL.md`. Resolve paths to `references/` and `scripts/` from that directory.

Optimize by evidence, not intuition. Preserve correctness first, then improve the bottleneck that measurements identify.

Target **C++20** unless the project explicitly uses another standard. Load bundled references on demand — do not read every reference file unless the task needs it.

For general C++20 style, see [`../cpp-coding/SKILL.md`](../cpp-coding/SKILL.md). For allocation and ownership design, see [`../cpp-memory-guide/SKILL.md`](../cpp-memory-guide/SKILL.md). For regression tests and Google Benchmark targets, see [`../cpp-testing/SKILL.md`](../cpp-testing/SKILL.md). For root-cause diagnosis before optimizing, see [`../debugging-guide/SKILL.md`](../debugging-guide/SKILL.md).

## Grounding

C++ performance is usually limited by one of: doing too much work, touching too much memory, waiting on synchronization or I/O, or blocking the CPU/compiler from executing efficiently. Measure first, then fix the limiting factor — not the code that merely looks slow.

| Limiting factor | Typical evidence | First reference |
|---|---|---|
| Excess work / algorithm | time grows faster than input; high instruction count | [cpp-language-patterns.md](references/cpp-language-patterns.md) |
| Memory / locality | cache misses; Backend Bound → Memory | [memory-layout-and-allocations.md](references/memory-layout-and-allocations.md) |
| Allocations | `malloc`/`new` in flamegraph or heap profile | [memory-layout-and-allocations.md](references/memory-layout-and-allocations.md), [cpp-memory-guide](../cpp-memory-guide/SKILL.md) |
| Branch prediction | high branch-miss rate; Bad Speculation in top-down | [cpp-language-patterns.md](references/cpp-language-patterns.md#branch-prediction), [measurement-and-benchmarking.md](references/measurement-and-benchmarking.md) |
| Contention / scaling | poor thread scaling; mutex/atomics in profile | [parallelism-and-contention.md](references/parallelism-and-contention.md) |
| False sharing | poor scaling with little logical sharing; `perf c2c` hits | [memory-layout-and-allocations.md](references/memory-layout-and-allocations.md#false-sharing) |
| I/O / syscalls | per-item open/close, logging, DB in profile | [cpp-language-patterns.md](references/cpp-language-patterns.md#io-and-syscalls) |
| Codegen / vectorization | missed vectorization; low IPC on compute-bound loops | [compiler-build-and-remarks.md](references/compiler-build-and-remarks.md) |

**Experience routing:** new to performance work — follow the default workflow and grounding table; use the hotspot index and [review-checklist.md](references/review-checklist.md) for diff review. Experienced — start at measurement or compiler references when the bottleneck class is already known.

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

6. **Load only the relevant reference** — see [Reference routing](#reference-routing) or the [hotspot index](#hotspot-index).

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

## Hotspot index

Quick map from profile evidence to references — apply fixes only after measurement.

| Evidence in profile | Likely cause | Read |
|---|---|---|
| `malloc` / `new` / allocator locks | allocation churn | [memory-layout-and-allocations.md](references/memory-layout-and-allocations.md) |
| cache misses; memory-bound top-down | layout, working set, pointer chasing | [memory-layout-and-allocations.md](references/memory-layout-and-allocations.md) |
| branch misses; Bad Speculation | unpredictable branches | [cpp-language-patterns.md](references/cpp-language-patterns.md#branch-prediction) |
| `std::map` / `std::list` / scattered pointers | poor locality containers | [memory-layout-and-allocations.md](references/memory-layout-and-allocations.md), [cpp-language-patterns.md](references/cpp-language-patterns.md) |
| repeated sort/parse/query in loops | excess work | [cpp-language-patterns.md](references/cpp-language-patterns.md) |
| `std::function` / virtual / `shared_ptr` in inner loops | type erasure or dispatch | [cpp-language-patterns.md](references/cpp-language-patterns.md) |
| mutex / atomics / poor thread scaling | lock contention | [parallelism-and-contention.md](references/parallelism-and-contention.md) |
| false sharing; cache-line bouncing | adjacent mutable fields | [memory-layout-and-allocations.md](references/memory-layout-and-allocations.md#false-sharing) |
| I/O / logging / DB per item | syscall or sync overhead | [cpp-language-patterns.md](references/cpp-language-patterns.md#io-and-syscalls) |
| missed vectorization / unexpected calls in loops | codegen | [compiler-build-and-remarks.md](references/compiler-build-and-remarks.md) |
| large binary / slow startup | static init, link bloat, cold-start stalls | [compiler-build-and-remarks.md](references/compiler-build-and-remarks.md#binary-size-and-startup) |

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

## Reference routing

| Task | Read |
|---|---|
| Baseline, benchmarks, perf counters, noise | [measurement-and-benchmarking.md](references/measurement-and-benchmarking.md) |
| Platform profiler commands | [tool-recipes.md](references/tool-recipes.md) |
| Build flags, remarks, vectorization, PGO/LTO/BOLT, binary size | [compiler-build-and-remarks.md](references/compiler-build-and-remarks.md) |
| Layout, SoA/AoS, allocations, false sharing | [memory-layout-and-allocations.md](references/memory-layout-and-allocations.md) |
| Threads, atomics, NUMA, scaling | [parallelism-and-contention.md](references/parallelism-and-contention.md) |
| Source smells and fixes | [cpp-language-patterns.md](references/cpp-language-patterns.md) |
| Diff review without running code | [review-checklist.md](references/review-checklist.md) |
| Final report | [performance-report.md](references/performance-report.md) |
