---
name: cpp-testing
description: Write, fix, and configure C++20 unit and integration tests with GoogleTest/GoogleMock, CMake/CTest, coverage, and sanitizers. Use when adding or updating C++ tests, fixing failing or flaky tests, setting up test targets, diagnosing gtest failures, or adding regression/coverage/sanitizer test builds — even if the user says "add tests" or "this test is flaky" without naming a framework.
---

# C++ Testing (C++20)

Resolve `<SKILL_ROOT>` as the directory containing **this** skill's `SKILL.md`. Resolve
paths to `references/` from that directory.

Write, fix, and gate C++ tests using **GoogleTest/GoogleMock** with **CMake/CTest**.
Test code uses the same **C++20** standard as production. Read bundled references on
demand — do not load all reference files unless the task requires them.

For test writing, fixing, and gating, this skill supersedes the brief testing section in
[cpp-coding](../cpp-coding/references/code-quality.md).

## Language Standard

- Target **C++20** (`-std=c++20` or CMake `cxx_std_20` on test targets).
- Test production code as consumers would — same ABI and standard as the library under test.
- Do **not** use C++23-only features in tests unless the project explicitly targets a newer
  standard.

## When to Use

- Writing new C++ tests or fixing existing tests
- Designing unit or integration coverage for C++ components
- Adding regression protection, CI gating, or coverage reporting
- Configuring CMake/CTest or GoogleTest discovery
- Investigating test failures or flaky behavior
- Enabling sanitizer builds for test targets (ASan, UBSan, TSan)

## When NOT to Use

- Implementing product features without test changes
- Large refactors unrelated to tests or coverage
- Performance tuning without test regressions to validate
- Non-C++ projects or non-test tasks

## Core Principles

1. **TDD when adding behavior** — RED → GREEN → REFACTOR
2. **Test pyramid** — mostly fast unit tests; integration tests only where fakes are
   insufficient (see [advanced-testing.md](references/advanced-testing.md))
3. **Deterministic and isolated** — no sleep-sync, unique temp paths, fixed RNG seeds
4. **Mock interactions, fake state** — GoogleMock for calls; fakes for stateful behavior
5. **Regression tests for bugs** — each fix gets a test that would have caught it
6. **Assert behavior** — tests fail when logic is wrong, not when implementation details
   change

## Workflow

### 1. Assess

- Read `CMakeLists.txt` — test targets, GoogleTest source (FetchContent/vcpkg/Conan),
  `gtest_discover_tests`, labels
- Note test layout (`tests/unit`, `tests/integration`, `testdata`)
- Identify failure type: compile, assertion, flake, sanitizer, coverage gap
- If only test sources change, skip CMake unless link or discovery errors appear

### 2. Write or Fix

- Follow TDD for new behavior; read routed references for patterns
- Prefer dependency injection over globals
- Match project naming and directory conventions

### 3. Run

```bash
cmake --build build -j
ctest --test-dir build -L unit --output-on-failure    # fast subset first
ctest --test-dir build --output-on-failure            # full suite
```

Use `--gtest_filter` for single-test reproduction and CTest `-R` for suite filters — see
[cmake-ctest.md](references/cmake-ctest.md) and
[debugging-flakiness.md](references/debugging-flakiness.md).

### 4. Debug

- Reproduce one test; add temporary logging; re-run under ASan/UBSan
- For flakes: `--gtest_repeat=N`; apply guardrails in debugging reference

### 5. Gate

Complete the two-part checklist in **Quick Completion Checklist** below before marking
test work done.

## Reference Routing

| Task | Read |
|------|------|
| TEST/TEST_F, mocks, parameterized/typed tests, exceptions, regression | [gtest-gmock.md](references/gtest-gmock.md) |
| CMake targets, CTest, discovery, labels, run commands | [cmake-ctest.md](references/cmake-ctest.md) |
| Coverage flags, ASan/UBSan/TSan test builds | [coverage-sanitizers.md](references/coverage-sanitizers.md) |
| Failures, flakes, pitfalls | [debugging-flakiness.md](references/debugging-flakiness.md) |
| Integration tests, fuzzing, property tests, test pyramid | [advanced-testing.md](references/advanced-testing.md) |
| Production code under test (RAII, ownership, CP.*) | [cpp-coding](../cpp-coding/SKILL.md) |

When a change spans multiple areas, read **every matching row** — e.g. concurrent tests
need [gtest-gmock.md](references/gtest-gmock.md),
[coverage-sanitizers.md](references/coverage-sanitizers.md) (TSAN), and
[debugging-flakiness.md](references/debugging-flakiness.md).

## Quick Completion Checklist

Two-part gate — complete **both** before marking test work done:

1. **Test quality** — checklist in
   [gtest-gmock.md](references/gtest-gmock.md#test-quality-checklist)
   (naming, AAA, determinism, regression tests, behavior assertions)
2. **Run and infrastructure** — checklist in
   [coverage-sanitizers.md](references/coverage-sanitizers.md#verification-checklist)
   (ctest pass, coverage/sanitizers per project, CI expectations)

The **Gate** workflow step requires **both** parts above — part 1 (test quality) and part 2
(run and infrastructure).

## External resources

- [GoogleTest documentation](https://google.github.io/googletest/)

Bundled references: see **Reference Routing** above.
