# Installation and Export

## Guideline

Install targets and headers with `install()`, then export **`install(EXPORT …)`** (or
`export(EXPORT …)` for build-tree packages) so downstreams consume **`find_package`** with
imported targets — using **relative** `INSTALL_INTERFACE` paths for relocatable packages.

## Rationale

Proper install/export turns your target graph into a redistributable CMake package with
namespaced imported targets (e.g. `mylib::mylib`).

## Example

```cmake
include(GNUInstallDirs)

install(TARGETS mylib
    EXPORT mylibTargets
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    INCLUDES DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)

install(DIRECTORY include/
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
    FILES_MATCHING PATTERN "*.h"
)

install(EXPORT mylibTargets
    FILE mylibTargets.cmake
    NAMESPACE mylib::
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/mylib
)

include(CMakePackageConfigHelpers)
write_basic_package_version_file(
    "${CMAKE_CURRENT_BINARY_DIR}/mylibConfigVersion.cmake"
    COMPATIBILITY SameMajorVersion
)

install(FILES
    cmake/mylibConfig.cmake
    "${CMAKE_CURRENT_BINARY_DIR}/mylibConfigVersion.cmake"
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/mylib
)
```

## Techniques

- **`install(TARGETS … EXPORT …)`** — record targets in an export set; set per-artifact
  `DESTINATION` (`RUNTIME`, `LIBRARY`, `ARCHIVE`).
- **`NAMESPACE`** — prefix exported targets (`mylib::`) to avoid collisions.
- **`INCLUDES DESTINATION`** — populate `INTERFACE_INCLUDE_DIRECTORIES` on installed IMPORTED
  targets relative to prefix.
- **Relocatable packages** — public includes use `$<INSTALL_INTERFACE:include>`, not absolute
  paths into the build machine.
- **`CMAKE_INSTALL_PREFIX`** — defaults to platform install root; set at configure time
  (`-DCMAKE_INSTALL_PREFIX=…`). Changing prefix after configure requires re-running CMake.

## Verify install

```bash
cmake --install build --prefix /tmp/mylib-install
cmake -DCMAKE_PREFIX_PATH=/tmp/mylib-install -S consumer -B consumer/build
```

## See also

- [generator-expressions.md](generator-expressions.md) — BUILD/INSTALL interface paths
- [find-package.md](find-package.md) — consuming installed packages
- [cmake-packages(7)](https://cmake.org/cmake/help/latest/manual/cmake-packages.7.html)
