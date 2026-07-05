# Code Quality (C++)

Language-agnostic quality principles adapted for C++. Naming conventions (NL.*) and
performance rules (Per.*) live in [core-guidelines.md](core-guidelines.md).

## Contents

- [Core principles](#core-principles)
- [Naming and readability](#naming-and-readability)
- [Comments and documentation](#comments-and-documentation)
- [Code smells](#code-smells)
- [Testing standards](#testing-standards)
- [Performance discipline](#performance-discipline)

## Core principles

### Readability first

Code is read more than written. Prefer clear names, small functions, and self-explanatory
structure over comments that restate the obvious.

### KISS (Keep It Simple)

- Use the simplest solution that meets requirements.
- Avoid clever templates or metaprogramming when a plain function suffices.
- Do not optimize without measurements (Per.1, Per.6 in core-guidelines).

### DRY (Don't Repeat Yourself)

- Extract repeated logic into named functions or templates.
- Share utilities across translation units via headers with clear interfaces.
- Avoid copy-paste branches that differ only slightly.

### YAGNI (You Aren't Gonna Need It)

- Don't build general frameworks for a single call site.
- Add abstraction when a second use case appears, not before.
- Prefer Rule of Zero over premature custom resource management.

## Naming and readability

Follow NL.* in [core-guidelines.md](core-guidelines.md). Summary:

- **`underscore_style`** for functions, variables, and types (NL.10).
- **Verbs for functions** that perform actions: `load_config`, `parse_header`,
  `is_valid()`.
- **Nouns for types**: `tcp_connection`, `parse_result`.
- **Member suffix `_`**: `host_`, `port_`.
- **No Hungarian notation** (NL.5): not `strName`, `iCount`.
- **ALL_CAPS for macros only** (NL.9); use `constexpr` for constants.

```cpp
// GOOD: intent-revealing
bool is_port_available(int port);
ParseResult parse_http_header(std::string_view raw);

// BAD: abbreviated or unclear
bool chk(int p);
auto go(std::string_view s);
```

## Comments and documentation

**Explain why, not what:**

```cpp
// Use exponential backoff to avoid overwhelming the API during outages
const auto delay_ms = std::min(1000 * (1 << retry_count), 30000);

// Deliberately not using std::async here — caller owns thread lifetime (CP.4)
void schedule_on_pool(Task task);
```

**Avoid:**

- Comments that duplicate the code (`// increment i`).
- Commented-out code left in production diffs.
- TODOs without owner or tracking reference.

**Public API documentation** — use Doxygen-style blocks for exported interfaces:

```cpp
/// Loads configuration from \a path. Throws ConfigError if the file is missing
/// or malformed.
/// @param path Filesystem path to a JSON or TOML config file.
/// @return Parsed configuration; never empty on success.
Config load_config(const std::filesystem::path& path);
```

## Code smells

### Long functions

Split functions that exceed ~40–50 lines or mix abstraction levels:

```cpp
// BAD: one function does validation, transform, and I/O
void process_file(const std::string& path);

// GOOD: orchestration + focused helpers
void process_file(const std::filesystem::path& path) {
    const auto data = read_and_validate(path);
    const auto result = transform(data);
    write_output(result);
}
```

### Deep nesting

Prefer early returns and guard clauses (ES.5):

```cpp
// BAD
if (user) {
    if (user->is_admin()) {
        if (resource) { /* ... */ }
    }
}

// GOOD
if (!user || !user->is_admin()) return;
if (!resource) return;
// ...
```

### Magic numbers

Use named `constexpr` constants (ES.45):

```cpp
constexpr int max_retries = 3;
constexpr auto debounce_delay = std::chrono::milliseconds{500};

if (retry_count > max_retries) { /* ... */ }
```

## Testing standards

For full test workflows (GoogleTest, CMake/CTest, coverage, sanitizers), use
[cpp-testing](../../cpp-testing/SKILL.md) — it supersedes this section for test work.

Use the **Arrange–Act–Assert** pattern:

```cpp
TEST(ParserTest, ReturnsEmptyWhenInputIsBlank) {
    // Arrange
    const std::string input;

    // Act
    const auto result = parse_tokens(input);

    // Assert
    EXPECT_TRUE(result.empty());
}
```

**Test naming** — describe behavior and condition:

- `ReturnsErrorWhenFileMissing`
- `MoveConstructorTransfersOwnership`
- `ConcurrentPushPopDoesNotDeadlock`

Prefer tests that would fail if the implementation were wrong — avoid mocks that only
assert "was called" without checking arguments.

## Performance discipline

- **Measure before optimizing** (Per.1, Per.6).
- **Design for measurement** — contiguous data, clear hot paths (Per.7, Per.19).
- **Compile-time work** when values are known at build time (Per.11).
- Link to [build-and-verification.md](build-and-verification.md) for profiling and
  sanitizer workflows.
