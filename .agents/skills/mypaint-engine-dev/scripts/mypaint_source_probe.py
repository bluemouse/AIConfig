#!/usr/bin/env python3
"""Probe local MyPaint/libmypaint checkouts for key painting-engine anchors.

This is a lightweight source-map sanity check. It verifies that expected files
and symbol strings exist, but it is not a semantic parser or build validator.
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable


MYP_CHECKS = {
    "gui/main.py": ["def main"],
    "gui/application.py": ["class Application"],
    "gui/document.py": ["class Document"],
    "gui/mode.py": ["ModeStack", "BrushworkModeMixin"],
    "gui/freehand.py": ["Freehand"],
    "lib/document.py": ["class Document", "sync_pending_changes"],
    "lib/command.py": ["Brushwork"],
    "lib/layer/tree.py": ["RootLayerStack", "symmetry"],
    "lib/layer/data.py": ["SurfaceBackedLayer", "stroke_to"],
    "lib/brush.py": ["class BrushInfo", "class Brush", "def stroke_to", "eotf"],
    "lib/brush.hpp": ["mypaint_brush_stroke_to"],
    "lib/python_brush.hpp": ["stroke_to"],
    "lib/tiledsurface.hpp": ["set_symmetry_state"],
}

LIB_CHECKS = {
    "mypaint-brush.c": [
        "struct MyPaintBrush",
        "settings_base_values_have_changed",
        "mypaint_brush_stroke_to",
    ],
    "mypaint-brush.h": ["mypaint_brush_stroke_to"],
    "mypaint-mapping.c": ["mypaint_mapping_calculate", "assert (n != 1)"],
    "mypaint-surface.h": [
        "draw_dab",
        "get_color",
        "begin_atomic",
        "end_atomic",
        "mypaint_surface_draw_dab",
    ],
    "mypaint-tiled-surface.h": [
        "MyPaintTiledSurface",
        "mypaint_tiled_surface_set_symmetry_state",
    ],
    "mypaint-tiled-surface.c": [
        "MYPAINT_TILE_SIZE",
        "process_op",
        "get_color",
        "begin_atomic",
    ],
    "mypaint-symmetry.c": ["mypaint_update_symmetry_state"],
    "brushmodes.c": ["BlendMode_Normal"],
    "helpers.c": ["rgb_to_hsv", "spectral"],
    "rng-double.c": ["rng_double"],
}


def check_files(root: Path, checks: dict[str, list[str]]) -> tuple[int, int]:
    passed = 0
    total = 0
    for rel, needles in checks.items():
        total += 1
        path = root / rel
        if not path.exists():
            print(f"FAIL missing {path}")
            continue
        try:
            text = path.read_text(errors="replace")
        except OSError as exc:
            print(f"FAIL unreadable {path}: {exc}")
            continue
        missing = [needle for needle in needles if needle not in text]
        if missing:
            print(f"FAIL {path}: missing anchors {missing}")
            continue
        print(f"OK   {path}")
        passed += 1
    return passed, total


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mypaint", type=Path, help="path to a mypaint checkout")
    parser.add_argument("--libmypaint", type=Path, help="path to a libmypaint checkout")
    args = parser.parse_args(argv)

    total_passed = 0
    total_checks = 0

    if args.mypaint:
        print("MyPaint application checks")
        passed, total = check_files(args.mypaint, MYP_CHECKS)
        total_passed += passed
        total_checks += total
    if args.libmypaint:
        print("libmypaint checks")
        passed, total = check_files(args.libmypaint, LIB_CHECKS)
        total_passed += passed
        total_checks += total

    if total_checks == 0:
        parser.error("provide --mypaint and/or --libmypaint")

    print(f"Summary: {total_passed}/{total_checks} checks passed")
    return 0 if total_passed == total_checks else 1


if __name__ == "__main__":
    raise SystemExit(main())
