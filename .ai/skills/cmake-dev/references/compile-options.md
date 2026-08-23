# Compile Options and Definitions

## Guideline

Set compiler flags, preprocessor definitions, and language standards with
`target_compile_options`, `target_compile_definitions`, and `target_compile_features` on
targets — not with directory-wide or global commands.

## Rationale

Target-scoped settings keep requirements local, composable, and correctly propagated via
PUBLIC/PRIVATE/INTERFACE.

## Example

```cmake
add_library(mylib src/mylib.cpp)

target_compile_options(mylib
    PRIVATE
        $<$<CXX_COMPILER_ID:GNU,Clang>:-Wall -Wextra -Wpedantic>
        $<$<CXX_COMPILER_ID:MSVC>:/W4 /permissive->
)

target_compile_definitions(mylib
    PUBLIC MYLIB_API_VERSION=2
    PRIVATE
        $<$<CONFIG:Debug>:MYLIB_DEBUG=1>
)

target_compile_features(mylib PUBLIC cxx_std_20)
```

## Techniques

- **`target_compile_features`** — prefer `cxx_std_20` (or project standard) on targets over
  global `CMAKE_CXX_STANDARD` when different targets need different standards.
- **`target_compile_definitions`** — use `PRIVATE` for implementation macros; `PUBLIC` only
  for macros in public headers.
- **Generator expressions** — gate flags by `$<CXX_COMPILER_ID:…>`, `$<CONFIG:Debug>`, or
  platform IDs for portable warning levels.
- **`target_compile_options`** — use `PRIVATE` for warnings; avoid PUBLIC warning flags that
  force downstream warning levels unless intentional.

## Anti-patterns

```cmake
# Legacy — avoid in new/modernized CMake
add_definitions(-DDEBUG)
include_directories(include)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall")
```

## See also

- [visibility-specifiers.md](visibility-specifiers.md) — PUBLIC/PRIVATE on options and defs
- [generator-expressions.md](generator-expressions.md) — conditional flags per config/toolchain
- [../cpp-coding/SKILL.md](../../cpp-coding/SKILL.md) — C++ language rules in source files
