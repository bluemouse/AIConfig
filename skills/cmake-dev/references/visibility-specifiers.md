# Visibility Specifiers

## Guideline

Attach includes, compile definitions, options, and link libraries with **PUBLIC**,
**PRIVATE**, or **INTERFACE** so usage requirements propagate only to the intended
consumers.

## Rationale

Visibility controls **transitive usage requirements**. PUBLIC items affect both the target
and its dependents; PRIVATE items affect only the target; INTERFACE items affect dependents
without being used when compiling the target itself (typical for header-only libraries).

## Semantics

| Keyword | Used when compiling target | Propagates to dependents |
|---------|---------------------------|--------------------------|
| `PRIVATE` | Yes | No |
| `INTERFACE` | No | Yes |
| `PUBLIC` | Yes | Yes |

From `target_link_libraries`: libraries after `PUBLIC` are linked to the target **and**
appear in the link interface; `PRIVATE` libraries link without exporting; `INTERFACE`
libraries export link requirements without linking the target.

## Example

```cmake
add_library(mylib src/mylib.cpp)

# Consumers need the public headers and API macro
target_include_directories(mylib PUBLIC include)
target_compile_definitions(mylib PUBLIC MYLIB_API=1)

# Internal headers and debug-only defs stay private
target_include_directories(mylib PRIVATE src/internal)
target_compile_definitions(mylib PRIVATE MYLIB_INTERNAL=1)

add_library(header_only INTERFACE)
target_include_directories(header_only INTERFACE include)

add_executable(app src/main.cpp)
target_link_libraries(app PRIVATE mylib header_only)
```

## Techniques

- Default implementation dependencies to **PRIVATE** (`fmt::fmt`, internal static libs).
- Use **PUBLIC** only for headers/defs/libs that consumers must see to compile/link against
  your API.
- Apply the **same visibility** consistently across includes, definitions, options, and links
  for a given dependency.
- Minimize PUBLIC surface to reduce transitive compile cost and accidental API leakage.

## Anti-patterns

```cmake
# INVALID: do not mix multiple visibility keywords on one item
# target_link_libraries(app PRIVATE mylib PUBLIC common)

# Prefer separate calls or a single visibility per group:
target_link_libraries(app PRIVATE mylib common)
```

## See also

- [target-types.md](target-types.md) — linking object and interface libraries
- [find-package.md](find-package.md) — imported targets already encode usage requirements
