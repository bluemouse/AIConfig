---
name: cpp-performance-guide
description: "Profile, benchmark, review, and optimize C/C++ runtime performance, latency, throughput, memory/cache locality, allocations, compiler codegen/vectorization, lock contention, binary size, startup, or compile time with reproducible measurements ('make it faster', Google Benchmark, perf, compiler remarks)."
---

# C++ Performance Guide

Resolve `<SKILL_ROOT>` as the directory containing **this** skill's `SKILL.md`. Resolve paths to `references/` and `scripts/` from that directory.

Optimize by evidence, not intuition. Preserve correctness first, then improve the bottleneck that measurements identify.

Target **C++20** unless the project explicitly uses another standard. Load bundled references on demand — do not read every reference file unless the task needs it.

For general C++20 style, see [`../cpp-coding/SKILL.md`](../cpp-coding/SKILL.md). For allocation and ownership design, see [`../cpp-memory-guide/SKILL.md`](../cpp-memory-guide/SKILL.md). For regression-test authoring, see [`../cpp-coding/SKILL.md`](../cpp-coding/SKILL.md); for Google Benchmark work, see [measurement-and-benchmarking.md](references/measurement-and-benchmarking.md) and the bundled scripts. For root-cause diagnosis before optimizing, see [`../debugging-guide/SKILL.md`](../debugging-guide/SKILL.md). For learning how performance-related code paths work without optimizing, see [`../code-professor/SKILL.md`](../code-professor/SKILL.md).

## Hotspot index

C++ performance is usually limited by one of: doing too much work, touching too much memory, waiting on synchronization or I/O, or blocking the CPU/compiler from executing efficiently. Measure first, then fix the limiting factor — not the code that merely looks slow. New to performance work — follow the default workflow and this table; for diff review without running code, see [review-checklist.md](references/review-checklist.md).

| Evidence in profile or measurement | Likely cause | Read |
|---|---|---|
| Time grows faster than input; high instruction count; repeated sort/parse/query in loops | Excess work / algorithmic complexity | [cpp-language-patterns.md](references/cpp-language-patterns.md) |
| Cache misses; Backend Bound → Memory; `std::map` / `std::list` / scattered pointers | Layout, working set, poor-locality containers, pointer chasing | [memory-layout-and-allocations.md](references/memory-layout-and-allocations.md) |
| `malloc` / `new` / allocator locks | Allocation churn | [memory-layout-and-allocations.md](references/memory-layout-and-allocations.md), [cpp-memory-guide](../cpp-memory-guide/SKILL.md) |
| High branch-miss rate; Bad Speculation in top-down | Unpredictable branches | [cpp-language-patterns.md](references/cpp-language-patterns.md#branch-prediction), [measurement-and-benchmarking.md](references/measurement-and-benchmarking.md) |
| Mutex / atomics / poor thread scaling | Lock contention | [parallelism-and-contention.md](references/parallelism-and-contention.md) |
| Poor scaling with little logical sharing; `perf c2c` hits; cache-line bouncing | False sharing from adjacent mutable fields | [memory-layout-and-allocations.md](references/memory-layout-and-allocations.md#false-sharing) |
| Per-item open/close, logging, DB in profile | Syscall or sync overhead | [cpp-language-patterns.md](references/cpp-language-patterns.md#io-and-syscalls) |
| Missed vectorization; low IPC on compute-bound loops; unexpected calls in loops | Codegen | [compiler-build-and-remarks.md](references/compiler-build-and-remarks.md) |
| `std::function` / virtual / `shared_ptr` in inner loops | Type erasure or dispatch | [cpp-language-patterns.md](references/cpp-language-patterns.md) |
| Large binary / slow startup | Static init, link bloat, cold-start stalls | [compiler-build-and-remarks.md](references/compiler-build-and-remarks.md#binary-size-and-startup) |

## When NOT to Use

- Non-C++ code or web-only performance (Core Web Vitals, frontend bundle size) — out of scope
- Active defect triage without a performance target — use **debugging-guide** first
- Memory leak, ownership design, or test-only work without a performance investigation — use **cpp-memory-guide** or **cpp-coding**

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
   - If the metric, workload, or acceptance threshold is undefined and the choice would change which bottleneck matters — average frame time versus worst-frame spikes, or a city scene versus startup path, for example — settle it with [../prompt-clarifier/SKILL.md](../prompt-clarifier/SKILL.md) before measuring, since an inferred target cannot satisfy the completion rule above.
   - When metric, workload, and threshold are all specified, proceed; state any remaining assumptions for platform, compiler, or hardware explicitly.

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

6. **Load only the relevant reference** — see the [hotspot index](#hotspot-index).

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
