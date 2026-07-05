# GoogleTest and GoogleMock

Unit test patterns for C++20 using GoogleTest/GoogleMock. For CMake setup see
[cmake-ctest.md](cmake-ctest.md).

## Contents

- [TDD workflow](#tdd-workflow)
- [Basic tests and fixtures](#basic-tests-and-fixtures)
- [Arrange-Act-Assert](#arrange-act-assert)
- [ASSERT vs EXPECT](#assert-vs-expect)
- [Mocks vs fakes](#mocks-vs-fakes)
- [Parameterized tests](#parameterized-tests)
- [Typed tests for templates](#typed-tests-for-templates)
- [Exceptions and noexcept](#exceptions-and-noexcept)
- [Move, copy, and RAII](#move-copy-and-raii)
- [Regression tests](#regression-tests)
- [Test quality checklist](#test-quality-checklist)

## TDD workflow

Follow RED → GREEN → REFACTOR:

1. **RED** — write a failing test for the new behavior
2. **GREEN** — smallest production change to pass
3. **REFACTOR** — clean up while tests stay green

```cpp
// tests/add_test.cpp
#include <gtest/gtest.h>

int add(int a, int b);  // production declaration

TEST(AddTest, AddsTwoNumbers) {  // RED
    EXPECT_EQ(add(2, 3), 5);
}

// src/add.cpp — GREEN
int add(int a, int b) { return a + b; }
```

## Basic tests and fixtures

```cpp
// tests/calculator_test.cpp
#include <gtest/gtest.h>

int add(int a, int b);

TEST(CalculatorTest, AddsTwoNumbers) {
    EXPECT_EQ(add(2, 3), 5);
}
```

Use `TEST_F` when multiple tests share setup:

```cpp
#include <gtest/gtest.h>
#include <memory>
#include <optional>
#include <string>

struct User { std::string name; };

class UserStore {
public:
    explicit UserStore(std::string path) : path_(std::move(path)) {}
    void seed(std::initializer_list<User> users) { users_ = users; }
    std::optional<User> find(const std::string& name) const {
        for (const auto& u : users_) {
            if (u.name == name) return u;
        }
        return std::nullopt;
    }
private:
    std::string path_;
    std::vector<User> users_;
};

class UserStoreTest : public ::testing::Test {
protected:
    void SetUp() override {
        store = std::make_unique<UserStore>(":memory:");
        store->seed({{"alice"}, {"bob"}});
    }

    std::unique_ptr<UserStore> store;
};

TEST_F(UserStoreTest, FindsExistingUser) {
    const auto user = store->find("alice");
    ASSERT_TRUE(user.has_value());
    EXPECT_EQ(user->name, "alice");
}
```

Prefer RAII in fixtures — resources created in `SetUp` are destroyed in `TearDown`/fixture
destruction automatically.

## Arrange-Act-Assert

Structure every test as AAA:

```cpp
TEST(ParserTest, ReturnsEmptyWhenInputIsBlank) {
    // Arrange
    const std::string input;

    // Act
    const auto tokens = parse_tokens(input);

    // Assert
    EXPECT_TRUE(tokens.empty());
}
```

Name tests as **BehaviorWhenCondition**: `ReturnsErrorWhenFileMissing`,
`MoveConstructorTransfersOwnership`, `ConcurrentPushPopDoesNotDeadlock`.

## ASSERT vs EXPECT

| Macro | Use when |
|-------|----------|
| `ASSERT_*` | Precondition — test cannot continue if it fails |
| `EXPECT_*` | Multiple independent checks in one test |

```cpp
TEST_F(UserStoreTest, FindsExistingUser) {
    const auto user = store->find("alice");
    ASSERT_TRUE(user.has_value());   // stop if null
    EXPECT_EQ(user->name, "alice"); // still useful if above passes
}
```

## Mocks vs fakes

- **Mock** (GoogleMock) — verify *interactions* (called with what args, how many times)
- **Fake** — lightweight working implementation for *stateful* behavior

```cpp
#include <gmock/gmock.h>
#include <gtest/gtest.h>
#include <string>

class Notifier {
public:
    virtual ~Notifier() = default;
    virtual void send(const std::string& message) = 0;
};

class MockNotifier : public Notifier {
public:
    MOCK_METHOD(void, send, (const std::string& message), (override));
};

class Service {
public:
    explicit Service(Notifier& notifier) : notifier_(notifier) {}
    void publish(const std::string& message) { notifier_.send(message); }
private:
    Notifier& notifier_;
};

TEST(ServiceTest, SendsNotifications) {
    MockNotifier notifier;
    Service service(notifier);

    EXPECT_CALL(notifier, send("hello")).Times(1);
    service.publish("hello");
}
```

Do not over-mock value objects or simple data — use real or fake instances.

## Parameterized tests

Use for boundary tables and input/output pairs:

```cpp
#include <gtest/gtest.h>

class ClampTest : public ::testing::TestWithParam<std::tuple<int, int, int, int>> {};

TEST_P(ClampTest, ClampsToRange) {
    const auto [value, lo, hi, expected] = GetParam();
    EXPECT_EQ(clamp(value, lo, hi), expected);
}

INSTANTIATE_TEST_SUITE_P(
    ClampCases,
    ClampTest,
    ::testing::Values(
        std::make_tuple(-1, 0, 10, 0),
        std::make_tuple(5, 0, 10, 5),
        std::make_tuple(99, 0, 10, 10)
    )
);
```

## Typed tests for templates

Test template code with multiple concrete types:

```cpp
#include <gtest/gtest.h>
#include <list>
#include <vector>

template<typename T>
class ContainerTest : public ::testing::Test {};

using ContainerTypes = ::testing::Types<std::vector<int>, std::list<int>>;
TYPED_TEST_SUITE(ContainerTest, ContainerTypes);

TYPED_TEST(ContainerTest, StartsEmpty) {
    T container;
    EXPECT_TRUE(container.empty());
}
```

For concept-constrained templates, use minimal types that satisfy the concept plus one
deliberate negative test at compile time (`static_assert`) when appropriate.

## Exceptions and noexcept

Test failure modes with typed exceptions:

```cpp
TEST(ConfigTest, ThrowsOnMissingFile) {
    EXPECT_THROW(load_config("nonexistent.json"), ConfigError);
}

TEST(ParseTest, NoThrowOnValidInput) {
    EXPECT_NO_THROW(parse("{}"));
}
```

**Death tests** (`EXPECT_DEATH`) — use sparingly for contract violations; behavior varies
by platform and build type. Prefer testing error returns or exceptions when possible.

## Move, copy, and RAII

```cpp
TEST(BufferTest, MoveTransfersOwnership) {
    Buffer a(10);
    a.write('x');
    Buffer b = std::move(a);
    EXPECT_EQ(b.size(), 10);
    EXPECT_TRUE(a.empty());  // moved-from state per type contract
}

TEST(BufferTest, SelfMoveAssignmentIsSafe) {
    Buffer buf(4);
    buf = std::move(buf);  // defined behavior for project's type
    SUCCEED();
}
```

Track side effects (files closed, handles released) with fakes or test doubles, not global
state.

## Regression tests

For every fixed bug, add a test named after the failure:

```cpp
// Regression: issue #452 — empty input caused divide-by-zero
TEST(StatsTest, Issue452_MeanOfEmptyReturnsZeroNotCrash) {
    EXPECT_EQ(mean({}), 0.0);
}
```

The test must fail on the old code and pass after the fix.

## Test quality checklist

Before marking test work complete (part 1 of the skill gate):

- [ ] Test names describe behavior and condition
- [ ] AAA structure is clear
- [ ] Tests assert **behavior**, not implementation details
- [ ] Tests would fail if the logic under test were wrong
- [ ] No `sleep` for synchronization — use latches, condition variables, or fakes
- [ ] No fixed temp paths — unique directories per test, cleaned up via RAII
- [ ] No wall-clock or network dependencies in unit tests
- [ ] Random inputs use a fixed seed unless testing randomness itself
- [ ] Mocks verify arguments/behavior, not just "was called"
- [ ] Regression test added for each bug fix
- [ ] Error and edge paths covered, not just happy path

Also complete part 2 in
[coverage-sanitizers.md](coverage-sanitizers.md#verification-checklist).
