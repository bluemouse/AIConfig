#!/usr/bin/env python3
"""Generate a compact Qt 6 Widgets/CMake plan for qt-dev tasks."""
from __future__ import annotations

import argparse
from typing import Iterable


def indented(items: Iterable[str], spaces: int = 4) -> str:
    prefix = " " * spaces
    return "\n".join(prefix + item for item in items)


def make_plan(name: str, mode: str, tests: bool) -> str:
    target = name.replace("-", "_")
    components = ["Core", "Gui", "Widgets"]
    if tests:
        components.append("Test")

    extra_sources: list[str] = []
    notes: list[str] = []

    if mode == "vulkan-window":
        extra_sources += [
            "src/viewport/VulkanViewportWindow.h",
            "src/viewport/VulkanViewportWindow.cpp",
            "src/viewport/VulkanViewportContainer.h",
            "src/viewport/VulkanViewportContainer.cpp",
        ]
        notes += [
            "Use QVulkanInstance in main/application bootstrap and keep it alive longer than every QWindow that uses it.",
            "Use QWidget::createWindowContainer() only for one primary viewport; account for stacking, focus, opacity, and native-child-window performance limits.",
        ]
    elif mode == "rhi-widget":
        extra_sources += [
            "src/viewport/RhiViewportWidget.h",
            "src/viewport/RhiViewportWidget.cpp",
        ]
        notes += [
            "Subclass QRhiWidget (public Widgets API); link Qt6::Widgets only — do not link private Qt modules.",
            "QRhiWidget can select Vulkan or Metal through Qt RHI, but renders through Qt-managed resources and a backing texture.",
            "Use QRhiWidget for previews or Qt-managed rendering, not for arbitrary native engine control.",
        ]
    else:
        notes.append("Use pure Widgets until a rendering viewport adapter is needed.")

    source_list = [
        "src/main.cpp",
        "src/app/MainWindow.h",
        "src/app/MainWindow.cpp",
        "src/app/MainWindow.ui",
        *extra_sources,
    ]

    cmake_lines = [
        "cmake_minimum_required(VERSION 3.21)",
        f"project({target} VERSION 0.1.0 LANGUAGES CXX)",
        "",
        "# Use 20 when the project allows; otherwise use 17 (Qt 6 minimum).",
        "set(CMAKE_CXX_STANDARD 20)",
        "set(CMAKE_CXX_STANDARD_REQUIRED ON)",
        "set(CMAKE_CXX_EXTENSIONS OFF)",
        "",
        f"find_package(Qt6 REQUIRED COMPONENTS {' '.join(components)})",
        "",
        "qt_standard_project_setup()",
        "",
        f"qt_add_executable({target}",
        indented(source_list, 4),
        ")",
        "",
        f"target_link_libraries({target}",
        "    PRIVATE",
        "        Qt6::Core",
        "        Qt6::Gui",
        "        Qt6::Widgets",
    ]
    cmake_lines += [
        ")",
        "",
        f"set_target_properties({target} PROPERTIES",
        "    WIN32_EXECUTABLE ON",
        "    MACOSX_BUNDLE ON",
        ")",
    ]

    if tests:
        notes.append(
            "For headless-safe smoke tests, set QT_QPA_PLATFORM=offscreen in add_test ENVIRONMENT."
        )
        cmake_lines += [
            "",
            "enable_testing()",
            f"qt_add_executable(tst_{target}_smoke",
            "    tests/tst_smoke.cpp",
            ")",
            f"target_link_libraries(tst_{target}_smoke PRIVATE Qt6::Test Qt6::Widgets)",
            f"add_test(NAME {target}_smoke COMMAND tst_{target}_smoke)",
        ]

    commands = [
        "Configure/build/test:",
        "  qt-cmake -S . -B build/debug -G Ninja -DCMAKE_BUILD_TYPE=Debug",
        "  cmake --build build/debug --parallel",
        "  ctest --test-dir build/debug --output-on-failure",
    ]

    return "\n".join([
        "# Qt 6 Widgets/CMake plan",
        "",
        "```cmake",
        "\n".join(cmake_lines),
        "```",
        "",
        "\n".join(commands),
        "",
        "Notes:",
        *[f"- {note}" for note in notes],
    ])


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a Qt 6 Widgets/CMake project plan.")
    parser.add_argument("--name", default="render-tool", help="project/target name")
    parser.add_argument("--mode", choices=["widgets", "vulkan-window", "rhi-widget"], default="widgets")
    parser.add_argument("--tests", action="store_true", help="include a Qt Test target")
    args = parser.parse_args()
    print(make_plan(args.name, args.mode, args.tests))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
