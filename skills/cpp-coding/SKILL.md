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

## When NOT to Use

- Non-C++ projects (use language-specific skills instead)
- Legacy C codebases that cannot adopt modern C++ features
- Embedded/bare-metal contexts where specific guidelines conflict with hardware constraints
  — adapt selectively and document tradeoffs
- Deep allocator/ownership design (arenas, PMR, caller-owned APIs, sanitizer memory debugging)
  — use [cpp-memory-guide](../cpp-memory-guide/SKILL.md)

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

## Reference Routing

| Task | Read |
|------|------|
| Classes, RAII, ownership, functions, error handling | [core-guidelines.md](references/core-guidelines.md) |
| Naming rules (NL.*), file/header conventions (SF.*) | [core-guidelines.md](references/core-guidelines.md) |
| Concepts, ranges, coroutines, threading, STL choices | [modern-cpp20.md](references/modern-cpp20.md) |
| Readability, code smells, tests, comments, KISS/DRY/YAGNI | [code-quality.md](references/code-quality.md) |
| Performance rules (Per.*) | [core-guidelines.md](references/core-guidelines.md#performance-per) |
| CMake, sanitizers, clang-tidy, coverage | [build-and-verification.md](references/build-and-verification.md) |
| Allocators, ownership APIs, move semantics, memory bugs | [cpp-memory-guide](../cpp-memory-guide/SKILL.md) |

When a change spans multiple areas, read **every matching row** — e.g. generic templates
need both [core-guidelines.md](references/core-guidelines.md) (T.*) and
[modern-cpp20.md](references/modern-cpp20.md); concurrent code needs core-guidelines (CP.*)
and modern-cpp20.

## Quick Completion Checklist

Two-part gate — complete **both** before marking C++ work done:

1. **Core Guidelines** — rule checklist in
   [core-guidelines.md](references/core-guidelines.md#quick-reference-checklist)
   (ownership, types, headers, concurrency, exceptions)
2. **Build and verification** — toolchain checklist in
   [build-and-verification.md](references/build-and-verification.md#verification-checklist)
   (C++20 build, warnings, static analysis, sanitizers, tests, coverage)

The Verify workflow step (above) is satisfied only when part 2 is complete.

## Resources

- [core-guidelines.md](references/core-guidelines.md) — C++ Core Guidelines (P, I, F, C, R,
  ES, E, Con, CP, T, SL, Enum, SF, NL, Per)
- [modern-cpp20.md](references/modern-cpp20.md) — C++20 language and library idioms
- [code-quality.md](references/code-quality.md) — Readability, smells, comments (brief
  testing notes; use [cpp-testing](../cpp-testing/SKILL.md) for test work)
- [build-and-verification.md](references/build-and-verification.md) — Toolchain and quality
  gates
- [cpp-memory-guide](../cpp-memory-guide/SKILL.md) — C++20 allocators, ownership, PMR, sanitizers (companion skill)
- [cpp-testing](../cpp-testing/SKILL.md) — C++20 GoogleTest/CMake testing (companion skill)

External reference: [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines)
