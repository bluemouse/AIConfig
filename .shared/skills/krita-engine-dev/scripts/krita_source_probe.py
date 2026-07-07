#!/usr/bin/env python3
"""Probe a local KDE/krita checkout for brush/stroke engine source anchors.

This script is intentionally lightweight and read-only. It checks whether common
files and critical symbols exist, then prints a Markdown report. It does not
compile Krita or require third-party Python packages.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable


@dataclass
class FileCheck:
    path: str
    exists: bool
    matched_patterns: list[str]
    missing_patterns: list[str]


CHECKS: dict[str, list[str]] = {
    "libs/ui/tool/kis_tool_freehand_helper.cpp": [
        "KisToolFreehandHelper::initPaintImpl",
        "KisResourcesSnapshot",
        "FreehandStrokeStrategy",
        "needsAirbrushing",
        "presetNeedsAsynchronousUpdates",
    ],
    "libs/ui/tool/strokes/freehand_stroke.cpp": [
        "FreehandStrokeStrategy",
        "doStrokeCallback",
        "issueSetDirtySignals",
    ],
    "libs/ui/tool/strokes/kis_painter_based_stroke_strategy.cpp": [
        "KisPainterBasedStrokeStrategy",
        "initStrokeCallback",
        "KisTransaction",
        "setupPainter",
    ],
    "libs/ui/tool/kis_resources_snapshot.cpp": [
        "KisResourcesSnapshot::setupPainter",
        "setPaintOpPreset",
        "setMirrorInformation",
        "cloneWithResourcesSnapshot",
    ],
    "libs/image/kis_image.cc": [
        "KisImage::startStroke",
        "KisUpdateScheduler",
        "requestProjectionUpdate",
    ],
    "libs/image/kis_update_scheduler.cpp": [
        "KisUpdateScheduler::startStroke",
        "KisStrokesQueue",
    ],
    "libs/image/kis_strokes_queue.cpp": [
        "KisStrokesQueue::startStroke",
        "LOD",
        "buddy",
    ],
    "libs/image/kis_painter.cc": [
        "KisPainter::setPaintOpPreset",
        "KisPainter::paintAt",
        "renderMirrorMask",
        "bltFixed",
    ],
    "libs/image/kis_painter_blt_multi_fixed.cpp": [
        "applyDevice",
        "bitBlt",
        "KoCompositeOp",
        "ParameterInfo",
    ],
    "libs/image/brushengine/kis_paintop.h": [
        "class KRITAIMAGE_EXPORT KisPaintOp",
        "paintAt(const KisPaintInformation",
        "updateSpacingImpl",
        "updateTimingImpl",
        "doAsynchronousUpdate",
    ],
    "libs/image/brushengine/kis_paint_information.h": [
        "class KRITAIMAGE_EXPORT KisPaintInformation",
        "pressure",
        "xTilt",
        "rotation",
        "currentTime",
    ],
    "plugins/paintops/defaultpaintops/brush/kis_brushop.cpp": [
        "KisBrushOp::paintAt",
        "KisDabRenderingExecutor",
        "DabRequestInfo",
        "effectiveSpacing",
        "KisBrushOp::doAsynchronousUpdate",
        "addMirroringJobs",
    ],
    "plugins/paintops/defaultpaintops/brush/KisDabRenderingExecutor.cpp": [
        "KisDabRenderingExecutor::addDab",
        "takeReadyDabs",
    ],
    "plugins/paintops/defaultpaintops/brush/KisDabRenderingQueue.cpp": [
        "KisDabRenderingQueue",
        "sequence",
    ],
    "plugins/paintops/libpaintop/KisDabCacheUtils.cpp": [
        "generateDab",
        "postProcessDab",
        "DabRequestInfo",
    ],
    "libs/brush/kis_brush.cpp": [
        "KisBrush::generateMaskAndApplyMaskOrCreateDab",
        "maskWidth",
        "maskHeight",
    ],
    "libs/image/kis_paint_device.cc": [
        "KisPaintDevice",
        "exactBounds",
        "extent",
    ],
    "libs/image/tiles3/kis_tiled_data_manager.cc": [
        "KisTiledDataManager",
        "bitBlt",
        "bitBltRough",
    ],
    "libs/image/tiles3/kis_tile_data.h": [
        "WIDTH",
        "HEIGHT",
    ],
    "libs/ui/canvas/kis_canvas2.cpp": [
        "createOpenGLCanvas",
        "createQPainterCanvas",
        "KisOpenGLCanvas2",
        "KisPrescaledProjection",
    ],
    "libs/ui/opengl/kis_opengl_canvas2.cpp": [
        "KisOpenGLCanvas2",
    ],
}


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def check_file(root: Path, rel_path: str, patterns: Iterable[str]) -> FileCheck:
    path = root / rel_path
    if not path.exists():
        return FileCheck(rel_path, False, [], list(patterns))
    text = read_text(path)
    matched: list[str] = []
    missing: list[str] = []
    for pattern in patterns:
        if pattern in text:
            matched.append(pattern)
        else:
            missing.append(pattern)
    return FileCheck(rel_path, True, matched, missing)


def render_markdown(root: Path, checks: list[FileCheck]) -> str:
    present = sum(1 for c in checks if c.exists)
    complete = sum(1 for c in checks if c.exists and not c.missing_patterns)
    lines = [
        "# Krita source probe report",
        "",
        f"root: `{root}`",
        f"files present: {present}/{len(checks)}",
        f"files with all expected patterns: {complete}/{len(checks)}",
        "",
        "## summary",
        "",
    ]

    for check in checks:
        status = "ok" if check.exists and not check.missing_patterns else "check"
        if not check.exists:
            status = "missing"
        lines.append(f"- **{status}** `{check.path}`")
        if check.matched_patterns:
            lines.append("  - matched: " + ", ".join(f"`{p}`" for p in check.matched_patterns))
        if check.missing_patterns:
            lines.append("  - missing: " + ", ".join(f"`{p}`" for p in check.missing_patterns))

    missing_files = [c.path for c in checks if not c.exists]
    if missing_files:
        lines.extend([
            "",
            "## next steps for missing paths",
            "",
            "Search by class or method names. Krita paths can move between versions.",
            "",
            "```bash",
            "rg \"KisToolFreehandHelper|KisBrushOp::paintAt|KisPaintOpRegistry|KisOpenGLCanvas2\" .",
            "```",
        ])

    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="probe a local krita checkout for brush/stroke source anchors")
    parser.add_argument("--root", required=True, help="path to the krita repository root")
    parser.add_argument("--json", action="store_true", help="print json instead of markdown")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    checks = [check_file(root, rel, patterns) for rel, patterns in CHECKS.items()]

    if args.json:
        print(json.dumps({"root": str(root), "checks": [asdict(c) for c in checks]}, indent=2))
    else:
        print(render_markdown(root, checks))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
