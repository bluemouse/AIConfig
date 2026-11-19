# Non-obvious CMake facts

Target-based usage requirements (PUBLIC/PRIVATE/INTERFACE propagation, target types,
`target_compile_options`/`_definitions`/`_features` scoping) are baseline knowledge —
this file holds only the rules implementations tend to get wrong.

## Visibility and options

- Keep visibility **consistent across includes, definitions, options, and links** for
  a given dependency — mixed visibility silently breaks usage requirements.
- Default implementation dependencies to **PRIVATE**; PUBLIC only for headers/defs/libs
  consumers must see to compile/link against your API. Minimize PUBLIC surface — it
  propagates transitive compile cost and can leak internal API.
- One visibility keyword per item group in `target_link_libraries`
  (`PRIVATE mylib PUBLIC common` is legal — each keyword governs the items after it —
  but confusing to read; prefer one group per call).
- Avoid PUBLIC warning flags — they force downstream warning levels. Gate flags per
  compiler/config with generator expressions (`$<CXX_COMPILER_ID:GNU,Clang>`,
  `$<CONFIG:Debug>`), never with `CMAKE_CXX_FLAGS` string surgery.
- Prefer `target_compile_features(mylib PUBLIC cxx_std_20)` over global
  `CMAKE_CXX_STANDARD` when targets need different standards.
- Never use the directory-scoped legacy commands in new code: `add_definitions`,
  `include_directories`, `link_directories`, `add_compile_options` with global effect.

## Target types

- Link **object libraries** with `target_link_libraries(consumer PRIVATE objects)` —
  CMake 3.12+ then propagates usage requirements and includes the objects in the
  consumer's link step.
- Let `BUILD_SHARED_LIBS` control default library type unless the project requires a
  fixed linkage model.
- Prefer **imported** targets from `find_package` (`Boost::system`) over creating new
  `SHARED` targets for external prebuilt libs unless wrapping is required — imported
  targets already encode usage requirements.

## See also

- [find-package.md](find-package.md) — search-order traps
- [fetchcontent.md](fetchcontent.md) — first-wins override rules
- [installation.md](installation.md) — relocatability and configure-time capture
- [generator-expressions.md](generator-expressions.md) — conditional flags per config/toolchain
- [../cpp-coding/SKILL.md](../../cpp-coding/SKILL.md) — C++ language rules in source files
