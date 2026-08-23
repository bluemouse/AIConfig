# Build and Verification

Toolchain setup, build practices, and quality gates for C++20 projects. Run these checks
before marking C++ work complete.

## Contents

- [C++20 toolchain](#c20-toolchain)
- [CMake practices](#cmake-practices)
- [Compiler warnings](#compiler-warnings)
- [Static analysis](#static-analysis)
- [Sanitizers and runtime checks](#sanitizers-and-runtime-checks)
- [Test coverage](#test-coverage)
- [Verification checklist](#verification-checklist)

## C++20 toolchain

- Require **C++20** (`-std=c++20` or CMake `cxx_std_20`).
- Confirm minimum compiler versions with the project (typical: GCC 10+, Clang 12+, MSVC
  2019 16.10+ — verify against project docs).
- Do not use C++23-only features unless the project explicitly upgrades.

## CMake practices

Prefer modern target-based CMake:

```cmake
cmake_minimum_required(VERSION 3.20)
project(my_app LANGUAGES CXX)

add_executable(my_app src/main.cpp)

target_compile_features(my_app PRIVATE cxx_std_20)

target_compile_options(my_app PRIVATE
    $<$<CXX_COMPILER_ID:GNU,Clang>:-Wall -Wextra -Wpedantic>
    $<$<CXX_COMPILER_ID:MSVC>:/W4>
)

# Sanitizers (optional target or CMAKE_CXX_FLAGS)
# target_compile_options(my_app PRIVATE -fsanitize=address,undefined)
# target_link_options(my_app PRIVATE -fsanitize=address,undefined)
```

- Use `target_link_libraries`, `target_include_directories` — avoid global `include_directories`.
- Pin dependencies via Conan, vcpkg, or FetchContent per project convention.
- Enable **LTO** (`-flto`) only when release binaries are profiled and size/speed gains justify build cost.

## Compiler warnings

Target: **zero warnings** on supported warning levels before merge.

| Flag | Purpose |
|------|---------|
| `-Wall -Wextra` (GCC/Clang) | Baseline warning set |
| `-Wpedantic` | Standards conformance |
| `/W4` (MSVC) | High warning level |
| `-Werror` | Treat warnings as errors (when CI supports it) |

Fix warnings at the source — don't blanket-disable with pragmas unless documented.

## Static analysis

Run at least one static analyzer in CI or before large merges:

| Tool | Typical use |
|------|-------------|
| **clang-tidy** | Core Guidelines checks, modernize, bugprone, performance |
| **cppcheck** | Additional cross-check, unused code, API misuse |

Example clang-tidy invocation:

```bash
clang-tidy src/*.cpp -- -std=c++20 -I include
```

Address findings or document justified suppressions with a comment referencing the rule.

## Sanitizers and runtime checks

| Check | Purpose |
|-------|---------|
| **AddressSanitizer (ASan)** | Heap/stack buffer overflows, use-after-free |
| **UndefinedBehaviorSanitizer (UBSan)** | Signed overflow, misaligned access, invalid shifts |
| **Valgrind** (Linux) | Leaks and invalid reads when ASan unavailable |

Build and test with sanitizers enabled:

```bash
cmake -DCMAKE_CXX_FLAGS="-fsanitize=address,undefined -fno-omit-frame-pointer" ..
cmake --build .
ctest --output-on-failure
```

All tests should pass clean — no reported leaks or undefined behavior.

When debugging a crash or sanitizer failure during implementation, follow the diagnostic
workflow in [native-debugging.md](native-debugging.md) and the root-cause method in
[debugging-guide](../../debugging-guide/SKILL.md).

## Test coverage

- Use **gcov/llvm-cov** or project CI coverage reporting.
- Prioritize coverage on error paths, ownership boundaries, and concurrency code.
- Coverage percentage alone is not sufficient — assert meaningful behavior (see
  [code-quality.md](code-quality.md)).

## Verification checklist

Before marking C++ work complete:

- [ ] Builds with C++20 (`cxx_std_20` / `-std=c++20`)
- [ ] Zero compiler warnings at project warning level
- [ ] clang-tidy / cppcheck clean (or documented suppressions)
- [ ] ASan + UBSan test runs pass (when available)
- [ ] No Valgrind leaks on critical paths (when applicable)
- [ ] Unit tests added or updated for changed behavior
- [ ] Coverage meets project threshold (if defined)
- [ ] Public API documented (Doxygen or project standard)
- [ ] Cross-platform or ABI notes updated if interfaces changed
