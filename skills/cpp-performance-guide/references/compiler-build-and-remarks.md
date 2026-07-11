# Compiler, Build, and Optimization Remarks

## Table of contents
- Build configurations
- Frame pointers and symbols
- Optimization remarks
- Assembly inspection
- Vectorization and aliasing
- LTO, PGO, AutoFDO, and BOLT
- Compile-time performance

## Build configurations

Use release-like builds for performance. For CMake:

```bash
cmake -S . -B build-rel -DCMAKE_BUILD_TYPE=RelWithDebInfo
cmake --build build-rel -j
```

For benchmarks intended for final reporting:

```bash
cmake -S . -B build-release -DCMAKE_BUILD_TYPE=Release
cmake --build build-release -j
```

Store important flags in target properties or presets, not only in shell history:

```cmake
target_compile_options(my_target PRIVATE
  $<$<CXX_COMPILER_ID:GNU,Clang>:-O3 -g -fno-omit-frame-pointer>
)
```

Do not use `-Ofast` by default. It can change floating-point and standards semantics. Use it only with explicit approval and correctness validation.

## Frame pointers and symbols

For Linux sampling profiles:

- `-g` maps samples to source lines.
- `-fno-omit-frame-pointer` improves frame-pointer call stacks.
- DWARF unwinding can work without frame pointers but costs more and can be incomplete.
- LBR call stacks are excellent when supported by CPU/kernel/tooling.

Verify the actual built binary flags when results are surprising.

## Optimization remarks

Clang:

```bash
clang++ -O3 -g -Rpass=.* -Rpass-missed=.* -Rpass-analysis=.* \
  -fsave-optimization-record source.cpp -c -o source.o
```

Useful filters:

```bash
-Rpass=loop-vectorize
-Rpass-missed=loop-vectorize
-Rpass-analysis=loop-vectorize
-Rpass=inline
-Rpass-missed=inline
```

GCC:

```bash
g++ -O3 -g -fopt-info-vec-optimized -fopt-info-vec-missed \
  -fopt-info-inline-optimized source.cpp -c -o source.o
```

Use `scripts/collect-compiler-remarks.sh` to wrap one compile command when possible.

## Assembly inspection

Inspect assembly only after profiling identifies a small hot kernel. Look for:

- vector registers (`xmm`, `ymm`, `zmm`) and SIMD instructions,
- unexpected calls inside inner loops,
- stack spills inside loops,
- bounds checks or iterator/debug overhead,
- missed inlining of tiny hot helpers,
- scalar loops where vectorization should be possible.

Local commands:

```bash
clang++ -O3 -std=c++20 -S -masm=intel kernel.cpp -o kernel.s
objdump -d -Mintel ./binary | less
llvm-objdump -d --symbolize-operands ./binary | less
```

Compiler Explorer is useful for small isolated codegen experiments, but confirm results in the real build.

## Vectorization and aliasing

The compiler vectorizes simple loops best. Help it by:

- using contiguous arrays, `std::span`, or pointer pairs,
- removing loop-carried dependencies,
- separating input and output buffers,
- making trip counts and alignment clear,
- avoiding virtual calls, hidden allocations, exceptions, and unpredictable branches inside the loop,
- using `__restrict__` on hot pointer parameters when the no-alias contract is true and documented.

Use `#pragma omp simd` only when the loop body is actually vectorization-safe. Relaxed math flags can change numerical behavior; treat them as a semantic change.

## LTO, PGO, AutoFDO, and BOLT

Use build/link tuning after algorithmic and source-level issues are addressed.

LTO/ThinLTO:

```cmake
set_property(TARGET my_target PROPERTY INTERPROCEDURAL_OPTIMIZATION TRUE)
```

Clang instrumented PGO sketch:

```bash
cmake -S . -B build-pgo-gen -DCMAKE_CXX_FLAGS="-fprofile-generate=$PWD/prof"
cmake --build build-pgo-gen -j
./build-pgo-gen/app representative-workload
llvm-profdata merge -output=code.profdata prof/*.profraw
cmake -S . -B build-pgo-use -DCMAKE_CXX_FLAGS="-fprofile-use=$PWD/code.profdata"
cmake --build build-pgo-use -j
```

BOLT can improve code layout for large binaries when profile data is representative. Use it late, with before/after evidence.

## Compile-time performance

When the performance problem is build time:

- measure with `ninja -d stats`, `-ftime-trace` (Clang), or build-system timing,
- reduce heavy includes in headers,
- use forward declarations where safe,
- isolate templates and generated code,
- use precompiled headers or modules only when they reduce real wall time,
- avoid unnecessary rebuild triggers,
- inspect link time separately from compile time.
