# Generator Expressions

## Guideline

Use generator expressions (`$<…>`) for settings that depend on build configuration,
toolchain, platform, or consumer context (build tree vs install tree).

## Rationale

Generator expressions are evaluated at **generate/build time**, enabling portable conditional
properties without separate configure branches for every compiler and config.

## Example

```cmake
target_include_directories(mylib PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)

target_compile_options(mylib PRIVATE
    $<$<CXX_COMPILER_ID:GNU,Clang>:-fno-rtti>
    $<$<CXX_COMPILER_ID:MSVC>:/GR->
)

target_compile_definitions(mylib PRIVATE
    $<$<CONFIG:Debug>:DEBUG_MODE=1>
    $<$<PLATFORM_ID:Linux>:LINUX_BUILD=1>
)
```

## Common expressions

| Expression | Purpose |
|------------|---------|
| `$<BUILD_INTERFACE:path>` | Include/link path for build-tree consumers |
| `$<INSTALL_INTERFACE:path>` | Path relative to install prefix for exports |
| `$<CONFIG:Debug>` | Per-configuration values |
| `$<CXX_COMPILER_ID:GNU,Clang>` | Compiler-specific flags |
| `$<PLATFORM_ID:Linux>` | OS-specific settings |
| `$<TARGET_GENEX_EVAL:…>` | Evaluate nested genex when debugging (CMake 3.27+) |

## Techniques

- **`message()` at configure time** prints unevaluated `$<…>` text — use build logs or
  `--trace-expand` sparingly when debugging genex output.
- **Quote arguments** containing `$<…>` when passing to commands to avoid semicolon splitting.
- **Nest carefully** — `$<$<BOOL:${VAR}>:value>` for boolean guards; avoid overly deep trees.
- Pair **BUILD_INTERFACE** and **INSTALL_INTERFACE** on public includes for installable
  libraries.

## See also

- [compile-options.md](compile-options.md) — genex on compile flags
- [installation.md](installation.md) — INSTALL_INTERFACE for relocatable exports
- [cmake-buildsystem(7)](https://cmake.org/cmake/help/latest/manual/cmake-buildsystem.7.html)
