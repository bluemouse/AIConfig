# Measurement and Benchmarking

## Table of contents
- Measurement contract
- Baseline hygiene
- End-to-end versus microbenchmark
- Google Benchmark pattern
- Linux counter triage
- Comparing results
- Noise control

## Measurement contract

Every performance answer must connect these items:

1. metric: latency, throughput, CPU time, allocations, RSS, frame time, or scaling efficiency
2. workload: input size, dataset, request mix, thread count, machine, and platform
3. build: compiler, flags, configuration, link mode, and debug-symbol/frame-pointer policy
4. baseline: before number and variance
5. evidence: profiler, counter, trace, or benchmark result
6. change: exactly what changed
7. after number: same workload and environment
8. correctness: tests that still pass

Do not compare different build types, machines, datasets, or thread counts unless the comparison explicitly studies those variables.

## Baseline hygiene

Use release-like builds:

- CMake: `-DCMAKE_BUILD_TYPE=RelWithDebInfo` for profiling or `Release` for final benchmark numbers.
- GCC/Clang: use `-O2` or `-O3`, `-DNDEBUG`, and debug info when profiling.
- Linux `perf` frame-pointer unwinding: add `-fno-omit-frame-pointer` to hot targets.
- Avoid `Debug`, ASan, TSan, UBSan, coverage, and instrumentation builds for final speed numbers.

Record:

```text
compiler + version:
standard library:
build type and flags:
commit / diff base:
input / workload:
thread count:
CPU model / OS:
frequency governor / power mode:
benchmark repetitions:
```

## End-to-end versus microbenchmark

Use end-to-end benchmarks for user-visible claims. Use microbenchmarks for:

- one tight kernel or data structure choice,
- allocator and copy behavior,
- branch/vectorization experiments,
- algorithm alternatives with controlled inputs,
- guarding against small regressions in known hot code.

Microbenchmark traps:

- optimizer removes the work,
- setup cost dominates the measured body,
- data size fits unrealistically in L1/L2 cache,
- branch predictor sees an unrealistically regular pattern,
- allocator/cache state differs from production,
- benchmark uses debug flags or sanitizer instrumentation.

## Google Benchmark pattern

Use Google Benchmark for isolated C++ microbenchmarks:

```cpp
#include <benchmark/benchmark.h>

static void BM_kernel(benchmark::State& state) {
    const int n = static_cast<int>(state.range(0));
    std::vector<float> input(n, 1.0f);
    std::vector<float> output(n);

    for (auto _ : state) {
        kernel(input.data(), output.data(), n);
        benchmark::DoNotOptimize(output.data());
        benchmark::ClobberMemory();
    }

    state.SetItemsProcessed(state.iterations() * n);
    state.SetBytesProcessed(state.iterations() * n * sizeof(float) * 2);
}
BENCHMARK(BM_kernel)->RangeMultiplier(2)->Range(64, 1 << 20);
BENCHMARK_MAIN();
```

Key idioms:

- `benchmark::DoNotOptimize(x)`: keep work observable.
- `benchmark::ClobberMemory()`: prevent reordering across memory effects when needed.
- `state.PauseTiming()` / `state.ResumeTiming()`: exclude setup when unavoidable.
- `--benchmark_repetitions=10`: reveal variance.
- `--benchmark_format=json`: create comparable artifacts.
- Check coefficient of variation; high variance weakens conclusions.

## Linux counter triage

Start with wall time plus counters:

```bash
perf stat -r 5 -d -- ./binary args
```

For top-down classification on supported CPUs:

```bash
perf stat -M TopdownL1 -- ./binary args      # Intel
perf stat -M PipelineL1 -- ./binary args     # AMD Zen 4+
```

Interpretation:

- Frontend Bound: instruction fetch/decode, i-cache, code size, branchy code, missed inlining/code layout.
- Bad Speculation: branch mispredicts, wasted work after wrong-path execution.
- Backend Bound -> Memory: cache misses, bandwidth, DRAM, pointer chasing, working set.
- Backend Bound -> Core: execution port pressure, dependency chains, non-vectorized arithmetic.
- Retiring high but slow wall time: algorithm does too much correct work.

Fallback counters when metrics are unavailable:

```bash
perf stat -r 5 -e cycles,instructions,branches,branch-misses,cache-references,cache-misses,context-switches,cpu-migrations,page-faults -- ./binary args
```

Ratios to inspect:

- IPC = instructions / cycles. Low IPC can indicate stalls, branches, memory, or dependencies.
- branch miss rate = branch-misses / branches. Above a few percent in hot code is suspicious.
- cache miss rate = cache-misses / cache-references. Interpret with workload and counter reliability.
- context switches and migrations. High values can invalidate CPU-bound conclusions.

## Comparing results

Use the same workload and build. Report both absolute numbers and percentage delta.

For Google Benchmark JSON (from `<SKILL_ROOT>/scripts/`):

```bash
./bench --benchmark_format=json --benchmark_repetitions=10 > before.json
./bench --benchmark_format=json --benchmark_repetitions=10 > after.json
python <SKILL_ROOT>/scripts/compare_benchmark_json.py before.json after.json
```

When using repetitions, prefer aggregate rows before comparing:

- pass `--benchmark_report_aggregates_only=true` to the bench binary, or
- filter JSON to `*_mean` rows only.

Comparing raw repetition output can trigger duplicate-name warnings in `compare_benchmark_json.py` and produce misleading deltas.

For shell command timing, prefer a tool such as `hyperfine` when available:

```bash
hyperfine --warmup 3 --runs 20 './binary args'
```

For latency services, compare distributions rather than one mean:

```text
p50, p95, p99, max, throughput, error rate, CPU, RSS
```

## Noise control

When numbers are noisy:

- use larger inputs or longer benchmark duration,
- increase repetitions and report variance,
- pin to a CPU (`taskset -c 2` on Linux),
- avoid CPU migration and competing background work,
- set performance governor where appropriate,
- monitor thermal throttling,
- avoid benchmarking inside oversubscribed VMs/containers,
- keep NUMA placement consistent (`numactl --cpunodebind=0 --membind=0`).

Do not hide noise. If variance is large, say the result is inconclusive.
