---
name: cmake-dev
description: Write, review, and refactor modern CMake 3.20+ build files for C/C++ projects using target-based builds. Use when editing CMakeLists.txt or *.cmake files; adding or linking targets; configuring PUBLIC/PRIVATE/INTERFACE visibility; integrating dependencies with find_package or FetchContent; wiring CTest; structuring multi-directory projects; applying generator expressions; or writing install/export rules — even if the user says "fix my build" without naming CMake.
---

# CMake Development

Resolve `<SKILL_ROOT>` as the directory containing **this** skill's `SKILL.md`. Resolve
paths to `references/` from that directory.

Write and review **CMake 3.20+** build files using **target-based** configuration. Read
bundled references on demand — do not load all reference files unless the task requires them.

## Requirements

- CMake ≥ 3.20; prefer target commands over directory/global state.
- Match the project's existing CMake style, minimum version, and dependency patterns before
  introducing new conventions.

## When to Use

- Authoring or reviewing `CMakeLists.txt` and `*.cmake` modules
- Creating libraries and executables with `add_library` / `add_executable`
- Linking dependencies with `target_link_libraries` and correct visibility
- Integrating packages via `find_package` or vendoring with `FetchContent`
- Enabling CTest, registering tests, and wiring test executables into the build graph
- Organizing multi-directory projects with `add_subdirectory`
- Applying generator expressions for build/install interfaces, configs, or toolchains
- Writing `install()` rules and `install(EXPORT …)` for downstream `find_package`

## When NOT to Use

- **C++ language, style, or Core Guidelines** — use
  [cpp-coding](../cpp-coding/SKILL.md) for idiomatic C++20 code, RAII, concepts, and
  refactoring production sources
- **GoogleTest/Mock test code, sanitizer/coverage test builds, flaky-test triage** — use
  [cpp-testing](../cpp-testing/SKILL.md) for `TEST`/`TEST_F` authoring, `gtest_discover_tests`,
  ASan/UBSan/TSan flags on test targets, and coverage reporting
- Pure CI YAML or non-CMake build systems (Meson, Bazel, MSBuild `.csproj`) with no CMake
  file changes
- Application feature work with no build-system edits

## Operating model

Treat this as a production CMake engineering skill. Optimize for **correct propagation of
usage requirements**, **reproducible dependencies**, and **maintainable project layout**.

Before editing nontrivial build files:

1. Read root and relevant subdirectory `CMakeLists.txt`, toolchain files, and preset files
   when present.
2. Note `cmake_minimum_required`, C/C++ standard policy, dependency sources (system,
   `find_package`, `FetchContent`, package managers), and existing target naming.
3. Prefer the smallest target-scoped change that fixes the build graph; avoid global
   `include_directories`, `link_libraries`, or `add_definitions`.
4. After changes, configure and build the affected targets, then run CTest when tests exist.

## Cross-cutting principles

1. **Targets first** — properties live on targets; globals are legacy exceptions only
2. **Visibility discipline** — PUBLIC propagates to consumers; minimize PUBLIC surface
3. **Imported targets** — link `Pkg::component` names from `find_package`, not raw `-l` paths
4. **Reproducible deps** — pin `GIT_TAG` / `URL_HASH` in `FetchContent_Declare`
5. **Verify before claiming** — run configure/build/ctest or state what was not verified

## Workflow

### 1. Assess

- Restate the outcome: new target, dependency, install layout, test wiring, or build fix.
- Inspect existing CMake layout, presets, and toolchain files.
- Read every matching row in [Reference routing](#reference-routing) before editing.

### 2. Implement

- Apply routed references for target types, visibility, options, dependencies, structure,
  generator expressions, testing hooks, and installation.
- Keep test *executable* targets and CTest registration here; route test *source* patterns to
  [cpp-testing](../cpp-testing/SKILL.md).
- Route C++ standard enforcement on production code to target properties; route C++ idioms in
  sources to [cpp-coding](../cpp-coding/SKILL.md).

### 3. Verify

From the build directory (adjust generator/path to the project):

```bash
cmake -S . -B build
cmake --build build -j
ctest --test-dir build --output-on-failure
```

For install/export work, also run `cmake --install build --prefix /tmp/prefix-check` when
safe. Report changed files, commands run, and remaining risks.

## Common gotchas

Verified against [cmake.org](https://cmake.org/cmake/help/latest/) — see [SOURCES.md](SOURCES.md).

- **`target_link_libraries` visibility** — `PRIVATE` links and propagates usage requirements
  only to the target; `PUBLIC` also exports link/usage to dependents; `INTERFACE` exports
  without linking to the target itself. Wrong visibility leaks transitive deps or hides needed
  interfaces.
- **`find_package` search order** — in Config mode, standard system prefixes are searched
  before `PATHS`; a system config can win over custom `PATHS`. Prefer `<Pkg>_ROOT`,
  `CMAKE_PREFIX_PATH`, or `find_package(… PATHS … NO_DEFAULT_PATH)` when forcing a prefix.
- **Generator expressions** — `$<CONFIG:Debug>` and `$<BUILD_INTERFACE:…>` evaluate at
  generate/build time; `message()` at configure time shows unevaluated expressions.
- **`CMAKE_INSTALL_PREFIX`** — captured at configure time; changing it after the first
  configure requires re-running CMake (often a clean build dir for relocatable packages).
- **`FetchContent` ordering** — declare dependencies before `FetchContent_MakeAvailable`;
  first `FetchContent_Declare` for a name wins in hierarchical projects.

## Reference routing

| Task | Read |
|------|------|
| Library/executable/object/interface target choice | [target-types.md](references/target-types.md) |
| PUBLIC / PRIVATE / INTERFACE on includes, links, defs, options | [visibility-specifiers.md](references/visibility-specifiers.md) |
| `target_compile_options`, definitions, `cxx_std_*` features | [compile-options.md](references/compile-options.md) |
| System packages, CONFIG vs MODULE, optional deps | [find-package.md](references/find-package.md) |
| Vendored deps, `FetchContent_Declare` / `MakeAvailable` | [fetchcontent.md](references/fetchcontent.md) |
| `enable_testing`, `add_test`, labels, CTest properties | [testing.md](references/testing.md) |
| Root layout, `add_subdirectory`, include interfaces | [project-structure.md](references/project-structure.md) |
| `$<BUILD_INTERFACE:…>`, `$<CONFIG:…>`, toolchain conditionals | [generator-expressions.md](references/generator-expressions.md) |
| `install(TARGETS …)`, `install(EXPORT …)`, relocatable packages | [installation.md](references/installation.md) |

When a change spans multiple areas, read **every matching row** — e.g. installable libraries
need [project-structure.md](references/project-structure.md), [generator-expressions.md](references/generator-expressions.md),
and [installation.md](references/installation.md).

## Quick completion checklist

Complete **both** before marking CMake work done:

1. **Build graph** — targets exist, visibility is minimal, no inappropriate global commands,
   dependencies use imported targets or well-scoped `FetchContent`
2. **Verification** — configure and build affected targets succeeded; CTest ran when tests
   were touched; install/export smoke-checked when install rules changed

Unverified configure/build/ctest must be stated explicitly.

## Output standards

For CMake answers:

- Provide complete, copy-pasteable snippets with `cmake_minimum_required` context when needed.
- Explain visibility and propagation when linking or setting include directories.
- Separate CMake build wiring from C++ source changes; point to companion skills when test
  code or C++ style is the main task.

For reviews:

- Prioritize propagation leaks, missing `PRIVATE` on impl deps, unpinned FetchContent,
  non-relocatable install interfaces, and missing test registration.
- Distinguish confirmed defects from stylistic preferences.

## Resources

- [target-types.md](references/target-types.md) — Static, shared, object, interface targets
- [visibility-specifiers.md](references/visibility-specifiers.md) — Usage requirement propagation
- [compile-options.md](references/compile-options.md) — Target-scoped flags and features
- [find-package.md](references/find-package.md) — Config and Module mode discovery
- [fetchcontent.md](references/fetchcontent.md) — Configure-time dependency population
- [testing.md](references/testing.md) — CTest integration (not GTest authoring)
- [project-structure.md](references/project-structure.md) — Multi-directory target layout
- [generator-expressions.md](references/generator-expressions.md) — Build-time conditionals
- [installation.md](references/installation.md) — Install and export for `find_package`
- [SOURCES.md](SOURCES.md) — Provenance and external references (read for attribution only)

External reference: [CMake documentation](https://cmake.org/cmake/help/latest/)
