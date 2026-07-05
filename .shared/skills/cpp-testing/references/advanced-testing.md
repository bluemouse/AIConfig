# Advanced Testing

Integration tests, optional fuzzing, and property-based testing. Use when unit tests and
[gtest-gmock.md](gtest-gmock.md) patterns are insufficient.

## Contents

- [Test pyramid](#test-pyramid)
- [Integration tests](#integration-tests)
- [Temp directory RAII](#temp-directory-raii)
- [Contract and API tests](#contract-and-api-tests)
- [constexpr and compile-time checks](#constexpr-and-compile-time-checks)
- [Fuzzing (optional)](#fuzzing-optional)
- [Property-based testing (optional)](#property-based-testing-optional)
- [Other frameworks](#other-frameworks)

## Test pyramid

Default effort distribution:

1. **Unit** (most) — fast, isolated, no I/O; live under `tests/unit/`
2. **Integration** (some) — real filesystem, processes, or multi-module wiring;
   `tests/integration/` with CTest label `integration`
3. **End-to-end** (few) — full stack; separate job, long timeout

Add integration tests when the change crosses process, network, or filesystem boundaries
that fakes cannot model faithfully.

## Integration tests

```cmake
gtest_discover_tests(integration_tests PROPERTIES LABELS "integration" TIMEOUT 120)
```

Keep integration tests deterministic: fixed testdata under `tests/testdata/`, no reliance
on machine-specific paths or external services without hermetic substitutes.

## Temp directory RAII

```cpp
#include <filesystem>
#include <gtest/gtest.h>

class TempDir {
public:
    TempDir() : path_(std::filesystem::temp_directory_path() /
                       ("gtest_" + std::to_string(++counter_))) {
        std::filesystem::create_directories(path_);
    }
    ~TempDir() { std::filesystem::remove_all(path_); }
    const std::filesystem::path& path() const { return path_; }
private:
    std::filesystem::path path_;
    static inline int counter_{0};
};

TEST(ImportTest, WritesOutputFile) {
    TempDir dir;
    const auto out = dir.path() / "out.txt";
    ASSERT_TRUE(import_fixture("input.json", out));
    EXPECT_TRUE(std::filesystem::exists(out));
}
```

## Contract and API tests

For public headers, test documented behavior consumers rely on:

- Include the header as a consumer would (`#include "mylib/widget.h"`)
- Test move-only/copyable contracts, exception guarantees, and `noexcept` where documented
- Avoid testing private implementation details

Breaking changes should fail contract tests before release.

## constexpr and compile-time checks

Use `static_assert` for compile-time paths; pair with runtime tests for runtime paths:

```cpp
static_assert(clamp(5, 0, 10) == 5);

TEST(ClampTest, RuntimeSameAsConstexpr) {
    EXPECT_EQ(clamp(5, 0, 10), 5);
}
```

## Fuzzing (optional)

Only when the project already supports **libFuzzer** or similar:

- Best for pure functions with minimal I/O
- One harness per entry point; check in corpus under `tests/fuzz/`

```cpp
#include <cstddef>
#include <cstdint>
#include <string>

extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {
    const std::string input(reinterpret_cast<const char*>(data), size);
    (void)parse_config(input);  // must not crash; validate invariants
    return 0;
}
```

Run fuzz targets in CI only if the project has infrastructure — do not add fuzzing as a
default requirement.

## Property-based testing (optional)

**RapidCheck** (or similar) when the project already depends on it:

- Express invariants: `parse(format(x)) == x`, `sort` is idempotent, etc.
- Complements table-driven `TEST_P`, not a replacement for regression tests

## Other frameworks

This skill defaults to **GoogleTest/GoogleMock**. If the project uses Catch2 or doctest,
follow project conventions — do not migrate frameworks unless asked.
