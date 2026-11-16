# Debugging Failures and Flakiness

Triage failing tests and eliminate nondeterministic behavior.

## Contents

- [Failure triage workflow](#failure-triage-workflow)
- [Flaky test guardrails](#flaky-test-guardrails)
- [Common pitfalls](#common-pitfalls)
- [When to disable vs fix](#when-to-disable-vs-fix)

## Failure triage workflow

1. **Reproduce one test** — narrow with gtest filter or CTest `-R`:

   ```bash
   ctest --test-dir build -R "UserStoreTest.FindsExistingUser" --output-on-failure
   ./build/example_tests --gtest_filter=UserStoreTest.FindsExistingUser
   ```

2. **Add scoped logging** around the failing assertion (remove before merge).

3. **Re-run under sanitizers** — ASan/UBSan often expose root cause faster than guesses:

   ```bash
   ctest --test-dir build-asan -R "FailingTest.*" --output-on-failure
   ```

4. **Expand scope** — once fixed, run full suite and relevant labels (`unit`, `integration`).

5. **Stress flaky suspects**:

   ```bash
   ./build/example_tests --gtest_filter=SuspiciousTest.* --gtest_repeat=100
   ```

## Flaky test guardrails

- **No `sleep` for synchronization** — use `std::condition_variable`, `std::latch`, or
  `std::barrier` (C++20) with bounded waits
- **Unique temp directories** per test — `std::filesystem::temp_directory_path() / unique_name`
- **Clean up via RAII** — destructor removes temp files even when assertions fail
- **No real time in unit tests** — inject a clock interface or use fake time sources
- **No network or live filesystem dependencies** in unit tests — use fakes or integration
  label
- **Deterministic RNG** — `std::mt19937 gen(42);` unless testing randomness itself
- **Reset shared state** in `SetUp`/`TearDown` or eliminate globals

```cpp
#include <barrier>
#include <latch>
#include <thread>

TEST(QueueTest, ProducerConsumer) {
    std::latch started{1};
    ThreadSafeQueue<int> queue;

    std::jthread consumer([&](std::stop_token st) {
        started.count_down();
        std::optional<int> value;
        ASSERT_TRUE(queue.wait_pop(value, st));
        EXPECT_EQ(*value, 42);
    });

    started.wait();
    queue.push(42);
}
```

## Common pitfalls

| Pitfall | Fix |
|---------|-----|
| Fixed temp path `/tmp/mytest` | Unique path per test; RAII cleanup |
| Wall-clock timeouts | Injectable clock; `wait_for` on condition variable |
| Flaky concurrency | Latch/barrier; TSAN build to find races |
| Hidden global state | Fixture reset or remove global |
| Over-mocking | Fake for state; mock only interactions |
| Missing sanitizer CI | ASan/UBSan on test job; TSAN for thread tests |
| Coverage on wrong build type | Same flags on lib + tests; Debug or consistent `-O` |
| Brittle log string match | Assert behavior, not log text, unless logging is the contract |

## When to disable vs fix

Use `DISABLED_` prefix only as a **temporary** measure with a tracked issue:

```cpp
TEST(QueueTest, DISABLED_Issue123_FlakyOnCI) { /* ... */ }
```

Do not merge disabled tests without an issue link and owner. Prefer fixing root cause or
moving the test to the correct tier (integration vs unit).

For persistent CI-only failures, check environment differences (locale, timezone, file limits)
before disabling.
