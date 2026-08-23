# Modern C++20 Features

C++20 idioms and patterns to prefer when writing or reviewing code. For ownership, RAII,
and Core Guidelines rules, see [core-guidelines.md](core-guidelines.md).

## Contents

- [Language features](#language-features)
- [Templates and concepts](#templates-and-concepts)
- [Memory and value semantics](#memory-and-value-semantics)
- [Standard library and ranges](#standard-library-and-ranges)
- [Concurrency](#concurrency)
- [Coroutines](#coroutines)
- [Modules (optional)](#modules-optional)
- [Out of scope (C++23+)](#out-of-scope-c23)

## Language features

Prefer these C++20 features over older equivalents:

| Feature | Use for |
|---------|---------|
| **Concepts** (`requires`, `std::integral`, custom concepts) | Constrain templates at compile time (T.10) |
| **Ranges & views** | Lazy pipelines, cleaner algorithms than raw iterators |
| **`<=>` (spaceship)** | Consistent comparisons; let compiler derive `==`, `<`, etc. |
| **Designated initializers** | Named struct initialization: `Point{.x = 1, .y = 2}` |
| **`constexpr` / `consteval`** | Compile-time computation where possible (Per.11) |
| **`std::span`** | Non-owning views into contiguous sequences |
| **`std::format`** | Type-safe formatting (prefer over `printf` / string concatenation) |
| **Structured bindings** | `auto [key, value] = pair;` for multi-return destructuring |
| **`if constexpr`** | Compile-time branches inside templates |

```cpp
#include <concepts>
#include <format>
#include <span>

template<std::integral T>
constexpr T clamp(T value, T lo, T hi) {
    return value < lo ? lo : (value > hi ? hi : value);
}

void log_reading(std::span<const double> samples) {
    std::format("count={}\n", samples.size());
}
```

## Templates and concepts

- Constrain every template argument with concepts (T.10, T.11) — avoid unconstrained templates
  in visible namespaces (T.47).
- Prefer `if constexpr` over SFINAE when a compile-time branch suffices.
- Use `using` aliases, not `typedef` (T.43).
- Overload function templates instead of specializing them (T.144).
- Reserve template metaprogramming for cases `constexpr` cannot solve (T.120).

```cpp
#include <concepts>
#include <ranges>

template<typename T>
concept Numeric = std::is_arithmetic_v<T>;

template<Numeric T>
T average(std::ranges::range auto const& values) {
    T sum{};
    std::size_t count = 0;
    for (const auto& v : values) {
        sum += static_cast<T>(v);
        ++count;
    }
    return count ? sum / static_cast<T>(count) : T{};
}
```

## Memory and value semantics

Apply Core Guidelines R.* and C.20/C.21; use C++20 move/copy rules:

- **Rule of Zero** by default — let compiler generate special members.
- **`std::unique_ptr`** for exclusive ownership; **`std::shared_ptr`** only when sharing is
  required (R.21).
- **`std::make_unique` / `std::make_shared`** — never naked `new` (R.11).
- Raw pointers are non-owning observers only (R.3).
- Rely on copy elision and move semantics; don't `std::move` everywhere "just because."
- Minimize heap allocation on hot paths; prefer stack/scoped objects (R.5).

See [core-guidelines.md](core-guidelines.md) for RAII examples and Rule of Five.

## Standard library and ranges

**Container selection** (SL.con.*):

- `std::vector` by default for dynamic sequences.
- `std::array` for fixed-size contiguous data.
- `std::string` to own text; `std::string_view` to observe (SL.str.*).

**Ranges** (C++20):

```cpp
#include <algorithm>
#include <ranges>
#include <vector>

std::vector<int> nums{3, 1, 4, 1, 5};

// Filter + transform without intermediate containers
auto evens_doubled = nums
    | std::views::filter([](int n) { return n % 2 == 0; })
    | std::views::transform([](int n) { return n * 2; });

// Prefer std::ranges algorithms
std::ranges::sort(nums);
```

- Use execution policies (`std::execution::par`) only after profiling shows benefit.
- Prefer `'\n'` over `std::endl` (SL.io.50).

## Concurrency

Follow CP.* in [core-guidelines.md](core-guidelines.md). C++20 additions:

- **`std::jthread`** — joins on destruction; prefer over detached `std::thread` (CP.26).
- **`std::scoped_lock`** — multiple mutexes without deadlock (CP.21).
- **`std::atomic`** with explicit memory orders only when profiling demands it.
- **Lock-free code** — last resort; requires deep expertise (CP.100).

```cpp
#include <jthread>
#include <mutex>
#include <scoped_lock>

class WorkerPool {
public:
    void start() {
        thread_ = std::jthread([this](std::stop_token st) {
            while (!st.stop_requested()) {
                process_next_job();
            }
        });
    }

private:
    std::jthread thread_;
    std::mutex queue_mutex_;
};
```

**Parallel algorithms**: `std::reduce`, `std::transform` with execution policies when data
is large and work per element is non-trivial.

## Coroutines

Use coroutines when asynchronous or generator-style control flow simplifies code that would
otherwise be callback- or state-machine-heavy:

- **`co_await`** for suspending on futures, I/O, or custom awaitables.
- **`co_yield`** for lazy generators.
- Prefer **`std::future` / callbacks** for simple one-shot async when coroutine infrastructure
  is not already in the project.

Keep coroutine types in dedicated modules/files — they affect ABI and readability.

## Modules (optional)

C++20 modules (`import std;`) reduce compile times and improve encapsulation, but toolchain
and ecosystem support varies. **Do not mandate modules** unless the project already uses them.
Stick with headers (`#include`) when portability or build integration is uncertain.

## Out of scope (C++23+)

Do not assume these unless the project explicitly targets C++23 or later:

- `std::expected` / `std::unexpected`
- `std::print` / `std::println` (use `std::format` in C++20)
- Reflection, metaclasses, or other experimental proposals
- `#embed`

When error handling without exceptions is needed in C++20, use `std::optional`, error codes,
or a project-specific result type — not `std::expected`.
