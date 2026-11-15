# Tool Recipes

## Table of contents
- Linux perf stat
- Linux perf record and flamegraphs
- Allocation and memory tools
- Tracy
- Valgrind tools
- macOS and iOS
- Windows
- Android
- Qt and desktop UI
- Game/rendering workloads
- Environments without PMU counters

## Linux perf stat

Counter triage:

```bash
scripts/run-perf-stat.sh ./binary args
```

Manual form:

```bash
perf stat -r 5 -d -- ./binary args
perf stat -e cycles,instructions,branches,branch-misses,cache-references,cache-misses -- ./binary args
```

Top-down metrics when supported:

```bash
perf stat -M TopdownL1 -- ./binary args
perf stat -M TopdownL2 -- ./binary args
perf stat -M PipelineL1 -- ./binary args
perf stat -M PipelineL2 -- ./binary args
```

Permissions:

- `kernel.perf_event_paranoid=2` usually allows per-process user-space profiling.
- Kernel/system-wide/uncore profiling may require lower values, root, or `CAP_PERFMON`.
- Some distros set stricter defaults; report the setting instead of guessing.

## Linux perf record and flamegraphs

Sampling profile:

```bash
scripts/run-perf-record.sh ./binary args
perf report
```

Manual flamegraph:

```bash
perf record -F 999 --call-graph fp -- ./binary args
perf script | stackcollapse-perf.pl | flamegraph.pl > flame.svg
```

If frame pointers are missing, try DWARF or LBR when supported:

```bash
perf record --call-graph dwarf -- ./binary args
perf record --call-graph lbr -- ./binary args
```

## Allocation and memory tools

Allocation profiles:

```bash
heaptrack ./binary args
heaptrack_gui heaptrack.*.gz
```

Valgrind massif:

```bash
valgrind --tool=massif ./binary args
ms_print massif.out.* | less
```

Cache simulation:

```bash
valgrind --tool=cachegrind ./binary args
cg_annotate cachegrind.out.* | less
```

Cachegrind and Callgrind are slow and distort timings, but useful when hardware counters are unavailable.

## Tracy

Use Tracy for long-running, frame-based, or production-like timeline analysis.

```cpp
#include <tracy/Tracy.hpp>

void update() {
    ZoneScoped;
    // work
}
```

Link `Tracy::TracyClient`, run the Tracy GUI, and connect to the process. Add zones around suspected frame phases, lock regions, allocator-heavy paths, and producer/consumer queues. Keep instrumentation out of final baseline comparisons unless it is always-on production instrumentation.

## Valgrind tools

Callgrind:

```bash
valgrind --tool=callgrind ./binary args
kcachegrind callgrind.out.*
```

Use Callgrind for deterministic instruction-level investigation when sampling is noisy or unavailable. Do not treat Callgrind wall time as native performance.

## macOS and iOS

Use Instruments:

- Time Profiler: CPU hotspots and call trees.
- Allocations: allocation churn, lifetime, and retain/release-like overhead in mixed stacks.
- System Trace: scheduling, locks, wakeups, I/O, and contention.
- Metal System Trace / GPU tools when C++ drives rendering work.

Build with dSYM/debug symbols and release optimization. For iOS, use a physical device for performance claims.

## Windows

Use:

- Visual Studio Profiler: CPU Usage, Instrumentation, Memory Usage, Concurrency Visualizer.
- Windows Performance Recorder/Analyzer (WPR/WPA): ETW traces for CPU, disk, scheduling, context switches, and system-wide behavior.
- Intel VTune or AMD uProf when available for PMU and microarchitecture analysis.

Use release builds with PDBs. Report compiler version, runtime library, and `/O2`/LTCG/PGO state.

## Android

Use:

- Android Studio Profiler for CPU/memory traces.
- Perfetto for system traces, scheduling, frame time, and binder/I/O interactions.
- Simpleperf for native CPU sampling:

```bash
adb shell simpleperf record -g --app your.package --duration 10
adb pull /data/local/tmp/perf.data .
simpleperf report -i perf.data
```

Use representative physical devices. Emulators are useful for functionality, not final performance claims.

## Qt and desktop UI

For Qt/C++ apps:

- Profile the event loop and identify main-thread stalls.
- Avoid expensive work in paint, layout, resize, and signal handlers.
- Batch model updates; avoid per-row signal storms.
- Move CPU work off the UI thread only when thread-safety and ownership are clear.
- Use platform profilers plus Qt Creator Analyzer when applicable.

## Game/rendering workloads

Separate CPU, GPU, and synchronization problems.

- CPU frame time: Tracy, Instruments, VTune, Superluminal, Visual Studio Profiler.
- GPU frame time: RenderDoc, Nsight Graphics, Radeon GPU Profiler, Xcode GPU tools, Metal System Trace.
- Look for CPU/GPU sync points, resource creation during frames, shader compilation, driver stalls, and per-frame allocations.

Do not optimize CPU code when the frame is GPU-bound unless CPU headroom is a separate requirement.

## Environments without PMU counters

If `perf stat` says counters are unsupported:

- use stable end-to-end benchmarks with repetitions,
- use Google Benchmark JSON for microbenchmarks,
- use Callgrind/Cachegrind for structural investigation,
- use heaptrack/massif for allocation and footprint,
- ask the user to run host-native profiler commands and provide outputs.
