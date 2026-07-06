# find_package

## Guideline

Locate prebuilt dependencies with `find_package`, then link **namespaced imported targets**
(`OpenSSL::SSL`, `Boost::filesystem`) rather than raw variables or `-l` flags when available.

## Rationale

Config packages and Find modules expose targets with correct usage requirements. Linking
imported targets keeps propagation and install/export layouts consistent.

## Modes

| Mode | How to request | Typical source |
|------|----------------|----------------|
| **Config** | `find_package(Foo CONFIG …)` or full signature | Upstream `FooConfig.cmake` |
| **Module** | default basic signature or `MODULE` keyword | CMake `FindFoo.cmake` |
| **Mixed** | basic signature (Module first, then Config fallback) | Either |

Use `CONFIG` when you know upstream ships a config package; use `MODULE` to restrict to Find
modules only.

## Example

```cmake
find_package(Boost 1.80 REQUIRED COMPONENTS system filesystem)

add_executable(app src/main.cpp)
target_link_libraries(app PRIVATE Boost::system Boost::filesystem)

find_package(OpenSSL)
if(OpenSSL_FOUND)
    target_link_libraries(app PRIVATE OpenSSL::SSL OpenSSL::Crypto)
    target_compile_definitions(app PRIVATE HAVE_OPENSSL=1)
endif()
```

## Forcing a prefix / avoiding system packages

Config-mode search consults `<Pkg>_ROOT`, `CMAKE_PREFIX_PATH`, and standard system locations
**before** the `PATHS` argument. A system-installed config can therefore win over custom
`PATHS` alone.

```cmake
# Prefer explicit roots:
cmake -DCMAKE_PREFIX_PATH=/opt/mylib ...

# Or restrict search to known paths:
find_package(MyLib CONFIG REQUIRED
    PATHS /opt/mylib/lib/cmake/MyLib
    NO_DEFAULT_PATH
)
```

Environment and cache variables `<Pkg>_ROOT` (CMake 3.12+) also prepend search paths.

## Techniques

- **`REQUIRED`** — fail configure if missing (mandatory deps).
- **`COMPONENTS` / `OPTIONAL_COMPONENTS`** — request package parts; check `<Pkg>_FOUND` or
  component variables for optional pieces.
- **`QUIET` / `REQUIRED`** — control error verbosity; optional deps omit `REQUIRED`.
- After success, prefer **`Pkg::target`** link lines; fall back to `Pkg_LIBRARIES` only for
  legacy Find modules without imported targets.

## See also

- [fetchcontent.md](fetchcontent.md) — vendoring when system packages are absent
- [installation.md](installation.md) — exporting your own config packages
- [cmake-packages(7)](https://cmake.org/cmake/help/latest/manual/cmake-packages.7.html)
