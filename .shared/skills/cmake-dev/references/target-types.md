# Target Types

## Guideline

Choose target types based on how artifacts are consumed: executables, static/shared
libraries, header-only interface libraries, or object libraries for reusable compiled units.

## Rationale

Modern CMake builds a graph of **targets** with propagated usage requirements. Picking the
right target type keeps linking, installation, and transitive dependencies predictable.

## Example

```cmake
# Default library type follows BUILD_SHARED_LIBS
add_library(mylib src/lib.cpp)

# Explicit static or shared
add_library(static_lib STATIC src/static.cpp)
add_library(shared_lib SHARED src/shared.cpp)

# Header-only: no compiled objects on this target
add_library(header_only INTERFACE)
target_include_directories(header_only INTERFACE include)

# Object library: compile once, link objects into other targets
add_library(objects OBJECT src/common.cpp)
target_link_libraries(mylib PRIVATE objects)

add_executable(app src/main.cpp)
target_link_libraries(app PRIVATE mylib)
```

## Techniques

| Type | When to use |
|------|-------------|
| `STATIC` / `SHARED` / default `add_library` | Compiled libraries with linkable artifacts |
| `INTERFACE` | Header-only or usage-requirement-only packages |
| `OBJECT` | Shared `.o` units across multiple targets (CMake 3.12+ object linking) |
| `add_executable` | Programs; `WIN32` / `MACOSX_BUNDLE` for GUI entry points |

- Let `BUILD_SHARED_LIBS` control default library type unless the project requires a fixed
  linkage model.
- Link object libraries with `target_link_libraries(consumer PRIVATE objects)` so usage
  requirements propagate; object files are included in the consumer's link step.
- Prefer **imported** targets from `find_package` (`Boost::system`) over creating new
  `SHARED` targets for external prebuilt libs unless wrapping is required.

## See also

- [visibility-specifiers.md](visibility-specifiers.md) — propagation when linking targets
- [installation.md](installation.md) — installing static/shared targets and exports
