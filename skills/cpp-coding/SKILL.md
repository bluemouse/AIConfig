---
name: cpp-coding
description: Write, review, and refactor modern C++20 code following C++ Core Guidelines — RAII, concepts, value semantics, and safe concurrency. Use when implementing C++ classes or functions, move constructors and move assignment, const-correct APIs, ranges and concept-constrained templates, reviewing C++ diffs for Core Guidelines violations, choosing between language alternatives (enum vs enum class, raw pointer vs smart pointer), refactoring C++ modules, or enforcing idiomatic C++20 style — even if the user says "C++ help" or "fix this C++ code" without naming a standard. Also use when writing or fixing C++ tests with GoogleTest/GoogleMock, CMake/CTest test targets, regression/coverage/sanitizer test builds, or failing and flaky gtest tests — even if the user says "add tests" or "this test is flaky" without naming a framework.
---

# C++ Coding (C++20)

Resolve `<SKILL_ROOT>` as the directory containing **this** skill's `SKILL.md`. Resolve
paths to `references/` from that directory.

Write and review C++ code against the **C++ Core Guidelines**, using **C++20** as the
baseline language standard. Read bundled references on demand — do not load all reference
files unless the task requires them.

## Language Standard

- Target **C++20** (`-std=c++20` or CMake `cxx_std_20`).
- Prefer C++20 features from [modern-cpp20.md](references/modern-cpp20.md) over older
  idioms.
- Do **not** use C++23-only features (e.g. `std::expected`, `std::print`) unless the
  project explicitly targets a newer standard.

## When NOT to Use

- Non-C++ projects (use language-specific skills instead)
- Legacy C codebases that cannot adopt modern C++ features
- Embedded/bare-metal contexts where specific guidelines conflict with hardware constraints
  — adapt selectively and document tradeoffs
- Allocator/ownership design, memory leaks, ownership conventions, or LSan/ASan
  allocation-site diagnosis — use [cpp-memory-guide](../cpp-memory-guide/SKILL.md)
- General defect investigation without a C++ coding focus — use
  [debugging-guide](../debugging-guide/SKILL.md) first for repro, hypotheses, and minimal fix
- Performance-only tuning without a correctness defect — use
  [cpp-performance-guide](../cpp-performance-guide/SKILL.md)
- Writing/fixing C++ tests is **in scope** (see **Testing** below) — but strict
  red-green-refactor coaching is [test-driven-dev-guide](../test-driven-dev-guide/SKILL.md)

## Cross-Cutting Principles

These themes apply to every C++ change:

1. **RAII everywhere** — bind resource lifetime to object lifetime; no leaked handles
2. **Immutability by default** — `const`/`constexpr` until mutation is required
3. **Type safety** — strong types, `enum class`, concepts; catch errors at compile time
4. **Express intent** — names, types, and interfaces communicate purpose
5. **Value semantics** — return by value; smart pointers for ownership; raw pointers as
   non-owning observers
6. **Minimize complexity** — KISS, DRY, YAGNI; simple code is correct code
   (F.2/F.3, ES.5)
7. **Measure before optimizing** — profile first; see [Per.*](references/core-guidelines.md#performance-per)
   in core-guidelines

## Workflow

### 1. Assess

Before writing or reviewing:

- Read `CMakeLists.txt` (or equivalent) — confirm **C++20**, compiler, and warning flags
- Read the repo's lint configuration (`.clang-tidy`, lint wrapper script, findings
  baseline) and follow its naming and check conventions — see
  [build-and-verification.md](references/build-and-verification.md#writing-lint-abiding-code)
- Note concurrency, real-time, or embedded constraints from context
- Identify whether the change touches ownership, threading, templates, or public API

### 2. Implement

- Apply [core-guidelines.md](references/core-guidelines.md) for classes, functions, RAII,
  error handling, and naming rules (NL.*)
- Apply [modern-cpp20.md](references/modern-cpp20.md) for concepts, ranges, concurrency,
  and modern idioms
- Match existing project style when it conflicts with defaults — document intentional
  deviations

### 3. Verify

Run the quality bar in [build-and-verification.md](references/build-and-verification.md):

- Builds clean at project warning level
- Static analysis and sanitizers pass when available
- Tests cover new behavior and important edge paths

### 4. Debug native failures (when applicable)

Crashes, sanitizer output, undefined behavior, or debugger-only state during C++ work:
start with [debugging-guide](../debugging-guide/SKILL.md) for reproduction and root-cause
method. After the fix is confirmed, add regression tests per **Testing** below and rerun
sanitizer-enabled builds per [build-and-verification.md](references/build-and-verification.md).

## Testing

Write and fix C++ tests with **GoogleTest/GoogleMock** wired through **CMake/CTest** —
in scope for this skill. Most test work is standard framework usage; the non-obvious
rules:

- **Never combine ASan and TSan in one build** — the runtimes are incompatible; use
  separate build directories (`build-asan`, `build-tsan`) and separate CI jobs
- **`GTest::gtest_main` vs `GTest::gtest`** — link `gtest_main` unless the test binary
  provides its own `main()` or needs custom entry-point initialization
- **Flake triage** — rerun the suspect with `--gtest_filter=... --gtest_repeat=100`;
  any failing iteration confirms nondeterminism before code inspection
- **Pin the GoogleTest version** (FetchContent `GIT_TAG` or versioned `find_package`) —
  behavior and deprecations shift across releases
- **Prefer `gtest_discover_tests` over one `add_test` per binary** — it registers each
  `TEST` as its own CTest entry for per-test filtering, labels, and failure reporting
- For failure triage, flaky-test guardrails, and the pitfalls table, read
  [debugging-flakiness.md](references/debugging-flakiness.md)

## Reference routing

| Task | Read |
|------|------|
| Classes, RAII, ownership, functions, error handling | [core-guidelines.md](references/core-guidelines.md) |
| Naming rules (NL.*), file/header conventions (SF.*) | [core-guidelines.md](references/core-guidelines.md) |
| Concepts, ranges, coroutines, threading, STL choices | [modern-cpp20.md](references/modern-cpp20.md) |
| Performance rules (Per.*) | [core-guidelines.md](references/core-guidelines.md#performance-per) |
| CMake, sanitizers, clang-tidy, coverage | [build-and-verification.md](references/build-and-verification.md) |
| GoogleTest/CTest test targets, flaky tests, pitfalls | **Testing** section + [debugging-flakiness.md](references/debugging-flakiness.md) |
| Allocators, ownership APIs, move semantics, memory bugs | [cpp-memory-guide](../cpp-memory-guide/SKILL.md) |
| Structured debugging method, repro, bisect, debug report | [debugging-guide](../debugging-guide/SKILL.md) |

Read a routing row only when you are about to act on that area with uncertain ground —
e.g. about to write generic templates with an unrecalled rule set, or unsure of the
project's lint conventions. When a change spans multiple areas, read the rows for the
areas you are about to touch.

## Quick completion checklist

Complete **both** parts before marking ordinary C++ work done:

1. **Core Guidelines** — rule checklist in
   [core-guidelines.md](references/core-guidelines.md#quick-reference-checklist)
   (ownership, types, headers, concurrency, exceptions)
2. **Build and verification** — toolchain checklist in
   [build-and-verification.md](references/build-and-verification.md#verification-checklist)
   (C++20 build, warnings, static analysis, sanitizers, tests, coverage)

The Verify workflow step (above) is satisfied when part 2 is complete. After a native
crash or UB fix, also satisfy debugging-guide's verification discipline before closing.

## Resources

- [core-guidelines.md](references/core-guidelines.md) — C++ Core Guidelines rule-ID
  checklist (P, I, F, C, R, ES, E, Con, CP, T, SL, Enum, SF, NL, Per)
- [modern-cpp20.md](references/modern-cpp20.md) — C++20 language and library idioms
- [build-and-verification.md](references/build-and-verification.md) — Toolchain and quality
  gates
- [debugging-flakiness.md](references/debugging-flakiness.md) — Test failure triage,
  flaky-test guardrails, and pitfalls table
- [cpp-memory-guide](../cpp-memory-guide/SKILL.md) — C++20 allocators, ownership, PMR (companion skill)
- [debugging-guide](../debugging-guide/SKILL.md) — Evidence-driven root-cause debugging before patching (companion skill)
- [cpp-performance-guide](../cpp-performance-guide/SKILL.md) — Measured C++ performance work when there is no correctness defect (companion skill)

External reference: [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines)

## Tool notes

Tool-specific mechanics are minimal for this skill — the body and references are
host-neutral.

C++ test work (GoogleTest, CMake/CTest, coverage, sanitizers) is handled by the **Testing**
section above.
