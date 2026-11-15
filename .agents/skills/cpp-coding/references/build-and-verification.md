# Build and Verification

Toolchain setup, build practices, and quality gates for C++20 projects. Run these checks
before marking C++ work complete.

## Contents

- [C++20 toolchain](#c20-toolchain)
- [CMake practices](#cmake-practices)
- [Compiler warnings](#compiler-warnings)
- [Static analysis](#static-analysis)
  - [Writing lint-abiding code](#writing-lint-abiding-code)
  - [Fast clang-tidy iteration on large codebases](#fast-clang-tidy-iteration-on-large-codebases)
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

### Writing lint-abiding code

Whether code passes clang-tidy is decided by the repository's own lint configuration, not
by generic guidelines. Write code that passes the repo's gate on the first run:

1. **Read the lint config before writing.** Check for `.clang-tidy` (or the project's
   lint wrapper config) and note the enabled check set and naming conventions —
   `readability-identifier-naming` options such as `ConstexprVariableCase` or
   `ParameterCase` are repo decisions that generic style rules cannot answer. Also check
   for a lint wrapper script (e.g. `tools/lint.sh`) and any findings baseline file it
   compares against.
2. **Follow neighboring code for conventions the config implies.** When the config
   specifies a naming case, confirm the concrete pattern (prefix or no prefix) against
   nearby declarations rather than guessing.
3. **Prefer fixing the code over suppressing.** Suppress only when the check is a known
   false positive or conflicts with a project convention, and scope the suppression as
   narrowly as possible.
4. **NOLINT discipline.** Place `// NOLINT(<check>)` on the same line as the flagged
   token — a NOLINT on an include line does not suppress a finding reported at a use
   site, and `NOLINTNEXTLINE` does not cover findings attributed to a different line.
   Add a brief rationale comment naming the check and the reason.
5. **Anticipate ripple effects.** Some fixes trigger new findings elsewhere — making a
   member function `static` flags call sites (`readability-static-accessed-through-instance`),
   and splitting a magic constant into a named one can leave the new constant unused.
   Re-run lint after such fixes before assuming clean.

### Fast clang-tidy iteration on large codebases

clang-tidy cost is dominated by per-TU front-end parsing, so full-project runs slow down
as the codebase grows. Two techniques keep iteration fast without weakening the final
gate:

**Lint only changed TUs.** Scope runs to the diff instead of the whole project, and use
the compilation database (`cmake -DCMAKE_EXPORT_COMPILE_COMMANDS=ON`) so each TU is
analyzed with its exact build flags:

```bash
# <base> = the repo's default branch (main, master, ...)
git diff --name-only --diff-filter=ACMR "$(git merge-base HEAD <base>)" \
  | grep '\.cpp$' | xargs -r clang-tidy -p build
```

- Map changed **headers** to their including TUs (via `ninja -t deps` or
  `clang-scan-deps`) and lint those TUs — linting a header standalone reports findings
  the TU-based gate never sees and misses findings from other includers.
- Only lint TUs that appear in the compilation database.
- Keep the full-project run (CI or pre-merge gate) as the authoritative check;
  changed-TU runs are for iteration.

**Parallelize across TUs.** Each clang-tidy process analyzes one TU single-threaded, so
run one worker per core for near-linear scaling. `run-clang-tidy` (shipped with LLVM)
batches files across workers and keeps warning output in a stable order:

```bash
run-clang-tidy -p build -j "$(nproc)" <changed-TUs...>
```

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
- [ ] clang-tidy / cppcheck clean (or documented suppressions) — changed TUs during
      iteration, full project at the pre-merge gate
- [ ] Lint config consulted before writing (`.clang-tidy`, wrapper script, baseline);
      any NOLINT carries a rationale
- [ ] ASan + UBSan test runs pass (when available)
- [ ] No Valgrind leaks on critical paths (when applicable)
- [ ] Unit tests added or updated for changed behavior
- [ ] Coverage meets project threshold (if defined)
- [ ] Public API documented (Doxygen or project standard)
- [ ] Cross-platform or ABI notes updated if interfaces changed
