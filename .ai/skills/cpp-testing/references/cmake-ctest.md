# CMake and CTest

Configure GoogleTest targets and CTest discovery for C++20 projects.

## Contents

- [Minimal setup](#minimal-setup)
- [Dependency sources](#dependency-sources)
- [Test target layout](#test-target-layout)
- [Discovery and labels](#discovery-and-labels)
- [Running tests](#running-tests)

## Minimal setup

```cmake
cmake_minimum_required(VERSION 3.20)
project(example LANGUAGES CXX)

include(FetchContent)
set(GTEST_VERSION v1.17.0)  # pin per project policy
FetchContent_Declare(
  googletest
  URL https://github.com/google/googletest/archive/refs/tags/${GTEST_VERSION}.zip
)
FetchContent_MakeAvailable(googletest)

add_library(example_lib src/calculator.cpp)
target_compile_features(example_lib PUBLIC cxx_std_20)

add_executable(example_tests
  tests/calculator_test.cpp
)
target_link_libraries(example_tests PRIVATE example_lib GTest::gtest_main GTest::gmock)
target_compile_features(example_tests PRIVATE cxx_std_20)

enable_testing()
include(GoogleTest)
gtest_discover_tests(example_tests)
```

Build and run:

```bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug
cmake --build build -j
ctest --test-dir build --output-on-failure
```

## Dependency sources

Use whichever the project already uses — do not introduce FetchContent if vcpkg/Conan is
standard:

| Method | When |
|--------|------|
| **FetchContent** | Greenfield or no package manager |
| **vcpkg** | `find_package(GTest CONFIG REQUIRED)` |
| **Conan** | `find_package(GTest REQUIRED)` per conanfile |

Always pin GoogleTest to a known version/tag.

## Test target layout

Recommended directory layout:

```
tests/
  unit/           # fast, isolated tests
  integration/    # filesystem, subprocess, multi-component
  testdata/       # fixture files (read-only)
```

Separate executables or one executable with labels — match project convention:

```cmake
add_executable(unit_tests tests/unit/calculator_test.cpp)
target_link_libraries(unit_tests PRIVATE my_lib GTest::gtest_main)
target_compile_features(unit_tests PRIVATE cxx_std_20)

add_executable(integration_tests tests/integration/import_test.cpp)
target_link_libraries(integration_tests PRIVATE my_lib GTest::gtest_main)
target_compile_features(integration_tests PRIVATE cxx_std_20)

gtest_discover_tests(unit_tests PROPERTIES LABELS "unit")
gtest_discover_tests(integration_tests PROPERTIES LABELS "integration")
```

Link **`GTest::gtest_main`** when tests provide `main` via gtest; link **`GTest::gtest`**
only when the project defines its own `main`.

## Discovery and labels

Prefer `gtest_discover_tests()` over manual `add_test()` — discovery stays in sync with
`TEST` macros.

```cmake
include(GoogleTest)
gtest_discover_tests(example_tests
  DISCOVERY_TIMEOUT 60
  PROPERTIES LABELS "unit"
)
```

Run subsets in CI:

```bash
ctest --test-dir build -L unit --output-on-failure
ctest --test-dir build -L integration --output-on-failure
```

## Running tests

**CTest:**

```bash
ctest --test-dir build --output-on-failure
ctest --test-dir build -R CalculatorTest
ctest --test-dir build -R "UserStoreTest.*" --output-on-failure
ctest --test-dir build -j 8   # parallel (when tests are isolated)
```

**GoogleTest filter** (direct executable):

```bash
./build/example_tests --gtest_filter=CalculatorTest.*
./build/example_tests --gtest_filter=UserStoreTest.FindsExistingUser
./build/example_tests --gtest_repeat=100 --gtest_filter=FlakyTest.*  # reproduce flake
```

CI pattern: run fast `unit` label first; full suite (and sanitizer build) on merge.
