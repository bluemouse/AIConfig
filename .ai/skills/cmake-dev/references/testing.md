# Testing with CTest

## Guideline

Enable CTest in CMake and register tests with `add_test` / `gtest_discover_tests` — keep
**test source authoring** (GoogleTest macros, mocks, sanitizer/coverage flags) in
[cpp-testing](../../cpp-testing/SKILL.md).

## Rationale

This skill owns **build-system test wiring**: test executables as targets, CTest registration,
labels, timeouts, and `WORKING_DIRECTORY`. Test implementation quality belongs in the C++
testing skill.

## Example

```cmake
include(CTest)
enable_testing()

add_executable(core_tests tests/core_test.cpp)
target_link_libraries(core_tests PRIVATE core GTest::gtest_main)

add_test(NAME core_tests COMMAND core_tests)
set_tests_properties(core_tests PROPERTIES TIMEOUT 60 LABELS "unit")

# When using GoogleTest and CMake 3.10+ discovery:
include(GoogleTest)
gtest_discover_tests(core_tests DISCOVERY_MODE PRE_TEST)
```

## Techniques

- **`enable_testing()`** — required in directory scope that registers tests (often root).
- **`add_test(NAME … COMMAND …)`** — register script or executable tests; set
  `WORKING_DIRECTORY` when runtime files live in the build tree.
- **`set_tests_properties`** — `TIMEOUT`, `LABELS`, `ENVIRONMENT`, `SKIP_REGULAR_EXPRESSION`.
- **Labels** — filter with `ctest -L unit`; combine with `--test-dir` in CMake 3.20+.
- **Separate test targets** — build test binaries separately from production targets; link
  `PRIVATE` to code under test.

## Boundary with cpp-testing

| Topic | cmake-dev | cpp-testing |
|-------|-----------|-------------|
| `add_executable` for tests, `add_test`, CTest labels | Yes | References CMake wiring |
| `TEST`/`TEST_F`, gmock, fixtures, sanitizer/coverage | Route there | Yes |
| Diagnosing assertion failures / flakiness | Route there | Yes |

## See also

- [project-structure.md](project-structure.md) — placing tests in subdirectories
- [../cpp-testing/SKILL.md](../../cpp-testing/SKILL.md) — GoogleTest, coverage, sanitizers
