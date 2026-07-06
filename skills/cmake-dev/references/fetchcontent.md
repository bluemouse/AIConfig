# FetchContent

## Guideline

Vendor dependencies at **configure time** with `FetchContent_Declare` followed by
`FetchContent_MakeAvailable` (or controlled `FetchContent_Populate` in advanced cases).

## Rationale

`FetchContent` makes sources available during configure so later commands can call
`add_subdirectory`, link imported targets, or include fetched modules — unlike
`ExternalProject_Add`, which downloads at build time.

## Example

```cmake
include(FetchContent)

FetchContent_Declare(
    fmt
    GIT_REPOSITORY https://github.com/fmtlib/fmt.git
    GIT_TAG        10.2.1
    GIT_SHALLOW    TRUE
)

FetchContent_MakeAvailable(fmt)

add_executable(app src/main.cpp)
target_link_libraries(app PRIVATE fmt::fmt)
```

## Techniques

- **`FetchContent_Declare`** — record download/update options; **first declare for a name
  wins** across the project hierarchy (parent can override child details if declared first).
- **Pin versions** — prefer immutable `GIT_TAG` commit hashes or `URL_HASH` for archives;
  branch names are not reproducible.
- **`FetchContent_MakeAvailable`** — populate if needed and add to the main build when the
  dependency is a CMake project.
- **`FetchContent_GetProperties` / `Populate`** — manual population when you must control
  ordering or avoid adding subdirectories automatically.
- **`FIND_PACKAGE_ARGS` / `OVERRIDE_FIND_PACKAGE`** (CMake 3.24+) — integrate with
  `find_package` fallbacks; see upstream docs before combining with existing package finds.

## Ordering

Declare all dependencies **before** calling `FetchContent_MakeAvailable`. Do not use fetched
targets in `add_subdirectory` until population completes.

## See also

- [find-package.md](find-package.md) — prefer system packages when suitable
- [project-structure.md](project-structure.md) — wiring fetched subprojects
- [../cpp-testing/SKILL.md](../../cpp-testing/SKILL.md) — GoogleTest FetchContent patterns in test code
