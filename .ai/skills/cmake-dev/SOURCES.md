# Sources

## CMake documentation (cmake.org)

- **URL:** https://cmake.org/cmake/help/latest/
- **Last reviewed:** 2026-07-06
- **Used for:**
  - `SKILL.md` → scope, workflow, gotchas, checklist
  - All `references/*.md` → command usage and modern target-based patterns
- **Aspects extracted:**
  - Target-based build model (CMake ≥ 3.20) → `references/project-structure.md`
  - Usage requirement propagation → `references/visibility-specifiers.md`

## cmake-buildsystem(7)

- **URL:** https://cmake.org/cmake/help/latest/manual/cmake-buildsystem.7.html
- **Last reviewed:** 2026-07-06
- **Used for:**
  - `SKILL.md` → cross-cutting principles, operating model
  - `references/target-types.md` → target categories and linking model
  - `references/visibility-specifiers.md` → transitive usage requirements
- **Aspects extracted:**
  - Target properties vs directory scope → `SKILL.md`, `references/project-structure.md`
  - Object library propagation → `references/target-types.md`

## cmake-packages(7)

- **URL:** https://cmake.org/cmake/help/latest/manual/cmake-packages.7.html
- **Last reviewed:** 2026-07-06
- **Used for:**
  - `references/find-package.md` → Config vs Find-module packages
  - `references/installation.md` → relocatable packages, export sets
- **Aspects extracted:**
  - IMPORTED targets from config packages → `references/find-package.md`
  - `INSTALL_INTERFACE` relative paths → `references/installation.md`, `references/generator-expressions.md`

## target_link_libraries

- **URL:** https://cmake.org/cmake/help/latest/command/target_link_libraries.html
- **Last reviewed:** 2026-07-06
- **Used for:**
  - `SKILL.md` → gotchas on PUBLIC/PRIVATE/INTERFACE
  - `references/visibility-specifiers.md` → linking with visibility keywords
- **Aspects extracted:**
  - PUBLIC/PRIVATE/INTERFACE semantics → `references/visibility-specifiers.md`
  - Object library linking behavior → `references/target-types.md`

## find_package

- **URL:** https://cmake.org/cmake/help/latest/command/find_package.html
- **Last reviewed:** 2026-07-06
- **Used for:**
  - `SKILL.md` → gotcha on search order vs `PATHS`
  - `references/find-package.md` → CONFIG/MODULE, components, `<Pkg>_ROOT`
- **Aspects extracted:**
  - Config-mode search order (system paths before `PATHS`) → `SKILL.md`, `references/find-package.md`
  - `CMAKE_PREFIX_PATH` and package root variables → `references/find-package.md`

## FetchContent module

- **URL:** https://cmake.org/cmake/help/latest/module/FetchContent.html
- **Last reviewed:** 2026-07-06
- **Used for:**
  - `references/fetchcontent.md` → Declare/MakeAvailable, pinning, hierarchy overrides
- **Aspects extracted:**
  - First declare wins; populate at configure time → `references/fetchcontent.md`
  - `GIT_TAG` hash pinning, `URL_HASH`, `FIND_PACKAGE_ARGS` → `references/fetchcontent.md`

## Template base (skills-ref/cmake-guide)

- **Path:** `skills-ref/cmake-guide/` (read-only input)
- **Last reviewed:** 2026-07-06
- **Used for:**
  - Initial section outline and reference filenames
- **Corrections applied during verify:**
  - Invalid mixed-visibility `target_link_libraries` example removed from
    `references/visibility-specifiers.md`
  - `find_package` PATHS/HINTS behavior refined per official search order
  - Testing reference scoped to CTest wiring; GTest authoring routed to `cpp-testing`
