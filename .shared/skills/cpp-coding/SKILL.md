---
name: cpp-coding
description: Write, review, and refactor modern C++20 code following C++ Core Guidelines — RAII, concepts, value semantics, and safe concurrency. Use when implementing C++ classes or functions, reviewing C++ diffs, choosing between language alternatives (enum vs enum class, raw pointer vs smart pointer), refactoring C++ modules, or enforcing idiomatic C++20 style — even if the user says "C++ help" or "fix this C++ code" without naming a standard.
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

## When to Use

- Writing new C++ code (classes, functions, templates)
- Reviewing or refactoring existing C++ code
- Making architectural decisions in C++ projects
- Enforcing consistent style across a C++ codebase
- Choosing between language features (e.g. `enum` vs `enum class`, raw pointer vs smart
  pointer)
- Diagnosing native C++ runtime failures while actively writing or reviewing C++ — when
  reproduction is already established or the failure is confined to code under edit; use
  [debugging-guide](../debugging-guide/SKILL.md) first if repro or root-cause workflow is
  not established (see workflow step 4 and [native-debugging.md](references/native-debugging.md))

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

## Cross-Cutting Principles

These themes apply to every C++ change:

1. **RAII everywhere** — bind resource lifetime to object lifetime; no leaked handles
2. **Immutability by default** — `const`/`constexpr` until mutation is required
3. **Type safety** — strong types, `enum class`, concepts; catch errors at compile time
4. **Express intent** — names, types, and interfaces communicate purpose
5. **Value semantics** — return by value; smart pointers for ownership; raw pointers as
   non-owning observers
6. **Minimize complexity** — KISS, DRY, YAGNI; simple code is correct code (expands
   core-guidelines principle 5)
7. **Measure before optimizing** — profile first; see [Per.*](references/core-guidelines.md#performance-per)
   in core-guidelines

## Workflow

### 1. Assess

Before writing or reviewing:

- Read `CMakeLists.txt` (or equivalent) — confirm **C++20**, compiler, and warning flags
- Note concurrency, real-time, or embedded constraints from context
- Identify whether the change touches ownership, threading, templates, or public API

### 2. Implement

- Apply [core-guidelines.md](references/core-guidelines.md) for classes, functions, RAII,
  error handling, and naming rules (NL.*)
- Apply [modern-cpp20.md](references/modern-cpp20.md) for concepts, ranges, concurrency,
  and modern idioms
- Apply [code-quality.md](references/code-quality.md) for readability, code smells, tests,
  and comments
- Match existing project style when it conflicts with defaults — document intentional
  deviations

### 3. Verify

Run the quality bar in [build-and-verification.md](references/build-and-verification.md):

- Builds clean at project warning level
- Static analysis and sanitizers pass when available
- Tests cover new behavior and important edge paths

### 4. Debug native failures (when applicable)

When the task involves crashes, sanitizer output, undefined behavior, or debugger-only
state while writing or reviewing C++:

1. If reproduction or root-cause workflow is not established, start with
   [debugging-guide](../debugging-guide/SKILL.md).
2. Apply C++ toolchain techniques in
   [native-debugging.md](references/native-debugging.md) — debug symbols, GDB/LLDB,
   sanitizers, core dumps, and typical lifetime/UB root causes.
3. After the fix is confirmed, add regression tests via
   [cpp-testing](../cpp-testing/SKILL.md) and rerun sanitizer-enabled builds per
   [build-and-verification.md](references/build-and-verification.md).

## Reference Routing

| Task | Read |
|------|------|
| Classes, RAII, ownership, functions, error handling | [core-guidelines.md](references/core-guidelines.md) |
| Naming rules (NL.*), file/header conventions (SF.*) | [core-guidelines.md](references/core-guidelines.md) |
| Concepts, ranges, coroutines, threading, STL choices | [modern-cpp20.md](references/modern-cpp20.md) |
| Readability, code smells, tests, comments, KISS/DRY/YAGNI | [code-quality.md](references/code-quality.md) |
| Performance rules (Per.*) | [core-guidelines.md](references/core-guidelines.md#performance-per) |
| CMake, sanitizers, clang-tidy, coverage | [build-and-verification.md](references/build-and-verification.md) |
| Native crashes, GDB/LLDB, sanitizers, UB, core dumps | [native-debugging.md](references/native-debugging.md) |
| Allocators, ownership APIs, move semantics, memory bugs | [cpp-memory-guide](../cpp-memory-guide/SKILL.md) |
| Structured debugging method, repro, bisect, debug report | [debugging-guide](../debugging-guide/SKILL.md) |

When a change spans multiple areas, read **every matching row** — e.g. generic templates
need both [core-guidelines.md](references/core-guidelines.md) (T.*) and
[modern-cpp20.md](references/modern-cpp20.md); concurrent code needs core-guidelines (CP.*)
and modern-cpp20.

## Quick Completion Checklist

Complete **both** parts before marking ordinary C++ work done; add part 3 when a native
crash or UB was fixed:

1. **Core Guidelines** — rule checklist in
   [core-guidelines.md](references/core-guidelines.md#quick-reference-checklist)
   (ownership, types, headers, concurrency, exceptions)
2. **Build and verification** — toolchain checklist in
   [build-and-verification.md](references/build-and-verification.md#verification-checklist)
   (C++20 build, warnings, static analysis, sanitizers, tests, coverage)
3. **Native crash/UB fix (when applicable)** — verification checklist in
   [native-debugging.md](references/native-debugging.md#verification)

The Verify workflow step (above) is satisfied when part 2 is complete; include part 3 when
workflow step 4 applied.

## Resources

- [core-guidelines.md](references/core-guidelines.md) — C++ Core Guidelines (P, I, F, C, R,
  ES, E, Con, CP, T, SL, Enum, SF, NL, Per)
- [modern-cpp20.md](references/modern-cpp20.md) — C++20 language and library idioms
- [code-quality.md](references/code-quality.md) — Readability, smells, comments (brief
  testing notes; use [cpp-testing](../cpp-testing/SKILL.md) for test work)
- [build-and-verification.md](references/build-and-verification.md) — Toolchain and quality
  gates
- [native-debugging.md](references/native-debugging.md) — Native C++ crash/UB diagnosis with
  debuggers and sanitizers (companion to debugging-guide)
- [cpp-memory-guide](../cpp-memory-guide/SKILL.md) — C++20 allocators, ownership, PMR (companion skill)
- [cpp-testing](../cpp-testing/SKILL.md) — C++20 GoogleTest/CMake testing (companion skill)
- [debugging-guide](../debugging-guide/SKILL.md) — Evidence-driven root-cause debugging before patching (companion skill)
- [cpp-performance-guide](../cpp-performance-guide/SKILL.md) — Measured C++ performance work when there is no correctness defect (companion skill)

External reference: [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines)
