# Coverage and Sanitizers

Coverage instrumentation and sanitizer builds for test targets. General toolchain gates
also live in
[cpp-coding build-and-verification](../../cpp-coding/references/build-and-verification.md).

## Contents

- [Coverage CMake options](#coverage-cmake-options)
- [GCC gcov and lcov](#gcc-gcov-and-lcov)
- [Clang llvm-cov](#clang-llvm-cov)
- [Sanitizer CMake options](#sanitizer-cmake-options)
- [Thread sanitizer for concurrency tests](#thread-sanitizer-for-concurrency-tests)
- [Verification checklist](#verification-checklist)

## Coverage CMake options

Apply flags per **test target**, not globally:

```cmake
option(ENABLE_COVERAGE "Enable coverage on test targets" OFF)

if(ENABLE_COVERAGE)
  if(CMAKE_CXX_COMPILER_ID MATCHES "GNU")
    target_compile_options(example_tests PRIVATE --coverage)
    target_link_options(example_tests PRIVATE --coverage)
  elseif(CMAKE_CXX_COMPILER_ID MATCHES "Clang")
    target_compile_options(example_tests PRIVATE -fprofile-instr-generate -fcoverage-mapping)
    target_link_options(example_tests PRIVATE -fprofile-instr-generate)
  endif()
endif()
```

Coverage measures test executables — ensure the same flags apply to linked production
libraries when measuring line coverage of library code.

## GCC gcov and lcov

```bash
cmake -S . -B build-cov -DENABLE_COVERAGE=ON -DCMAKE_BUILD_TYPE=Debug
cmake --build build-cov -j
ctest --test-dir build-cov --output-on-failure

lcov --capture --directory build-cov --output-file coverage.info
lcov --remove coverage.info '/usr/*' '*/tests/*' --output-file coverage.info
genhtml coverage.info --output-directory coverage
```

Prioritize error paths, ownership boundaries, and concurrency code — percentage alone is
not sufficient.

## Clang llvm-cov

```bash
cmake -S . -B build-llvm -DENABLE_COVERAGE=ON -DCMAKE_CXX_COMPILER=clang++
cmake --build build-llvm -j
LLVM_PROFILE_FILE="build-llvm/default.profraw" ctest --test-dir build-llvm --output-on-failure

llvm-profdata merge -sparse build-llvm/default.profraw -o build-llvm/default.profdata
llvm-cov report build-llvm/example_tests -instr-profile=build-llvm/default.profdata
llvm-cov show build-llvm/example_tests -instr-profile=build-llvm/default.profdata -format=html \
  -output-dir coverage-html
```

## Sanitizer CMake options

Scope sanitizers to test (and optionally library) targets:

```cmake
option(ENABLE_ASAN "AddressSanitizer on tests" OFF)
option(ENABLE_UBSAN "UndefinedBehaviorSanitizer on tests" OFF)
option(ENABLE_TSAN "ThreadSanitizer on tests" OFF)

function(apply_sanitizers target)
  if(ENABLE_ASAN)
    target_compile_options(${target} PRIVATE -fsanitize=address -fno-omit-frame-pointer)
    target_link_options(${target} PRIVATE -fsanitize=address)
  endif()
  if(ENABLE_UBSAN)
    target_compile_options(${target} PRIVATE -fsanitize=undefined -fno-omit-frame-pointer)
    target_link_options(${target} PRIVATE -fsanitize=undefined)
  endif()
  if(ENABLE_TSAN)
    target_compile_options(${target} PRIVATE -fsanitize=thread)
    target_link_options(${target} PRIVATE -fsanitize=thread)
  endif()
endfunction()

apply_sanitizers(example_tests)
```

Do not combine ASan and TSan in one build. Run sanitizer jobs as separate CI configurations.

```bash
cmake -S . -B build-asan -DENABLE_ASAN=ON -DENABLE_UBSAN=ON
cmake --build build-asan -j
ctest --test-dir build-asan --output-on-failure
```

## Thread sanitizer for concurrency tests

Run concurrent test suites under TSAN:

```bash
cmake -S . -B build-tsan -DENABLE_TSAN=ON
cmake --build build-tsan -j
ctest --test-dir build-tsan -L unit -R "Concurrent|Thread|Async" --output-on-failure
```

Pair TSAN runs with deterministic synchronization in tests (see
[debugging-flakiness.md](debugging-flakiness.md)) — no `sleep` for correctness.

## Verification checklist

Before marking test infrastructure work complete (part 2 of the skill gate):

- [ ] Tests build with C++20 (`cxx_std_20`)
- [ ] `ctest --output-on-failure` passes locally
- [ ] New/changed behavior has added or updated tests
- [ ] Coverage generated when project requires it; thresholds met if defined
- [ ] ASan + UBSan test run clean (when available in CI)
- [ ] TSAN run clean for concurrency-related tests (when available)
- [ ] Sanitizer and coverage use target-level flags, not undocumented globals
- [ ] CI runs fast unit subset before full/sanitizer jobs

Part 1 (test quality): [gtest-gmock.md#test-quality-checklist](gtest-gmock.md#test-quality-checklist).
