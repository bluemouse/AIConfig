# Project Structure

## Guideline

Organize CMake 3.20+ projects around **targets** declared in root and subdirectory
`CMakeLists.txt` files, with `add_subdirectory` for components and generator-expression
include interfaces for build vs install consumers.

## Rationale

A clear target graph scales to multi-directory repos, superbuilds, and installable packages
without global directory properties.

## Example

```cmake
cmake_minimum_required(VERSION 3.20)
project(demo VERSION 1.0.0 DESCRIPTION "Example" LANGUAGES CXX)

add_library(core src/core.cpp src/utils.cpp)
target_include_directories(core PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)
target_compile_features(core PUBLIC cxx_std_20)

add_executable(app src/main.cpp)
target_link_libraries(app PRIVATE core)

include(CTest)
enable_testing()
add_subdirectory(tests)
```

```cmake
# tests/CMakeLists.txt
add_executable(core_test core_test.cpp)
target_link_libraries(core_test PRIVATE core GTest::gtest_main)
add_test(NAME core_test COMMAND core_test)
```

## Techniques

- **`cmake_minimum_required(VERSION 3.20)`** — baseline for modern target commands and CTest
  `--test-dir`.
- **`project(… LANGUAGES …)`** — declare languages once at root; use `enable_language` only
  when needed in rare layouts.
- **`add_subdirectory`** — delegate component targets; avoid repeating fetch/find logic in
  every child — centralize dependencies at the highest sensible level.
- **`target_include_directories` with `$<BUILD_INTERFACE:…>` / `$<INSTALL_INTERFACE:…>`** —
  separate build-tree paths from installed layout (required for relocatable packages).
- **Prefer `target_compile_features`** over global `CMAKE_CXX_STANDARD` when targets differ.

## Layout conventions

```text
project/
├── CMakeLists.txt          # project(), dependencies, add_subdirectory
├── cmake/                  # optional: modules, toolchains
├── include/project/        # public headers
├── src/                    # library and app sources
└── tests/CMakeLists.txt    # test targets + add_test
```

## See also

- [target-types.md](target-types.md) — libraries and executables in subdirs
- [generator-expressions.md](generator-expressions.md) — BUILD/INSTALL interfaces
- [installation.md](installation.md) — exporting installed layouts
