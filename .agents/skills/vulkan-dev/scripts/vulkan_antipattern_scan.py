#!/usr/bin/env python3
"""Lightweight Vulkan C/C++ anti-pattern scanner.

This script is intentionally conservative: it flags patterns worth human review; it
is not a validator and does not prove code invalid.
"""
from __future__ import annotations

import argparse
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

SOURCE_EXTS = {".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx", ".inl", ".glsl", ".hlsl"}

@dataclass(frozen=True)
class Rule:
    name: str
    pattern: re.Pattern[str]
    severity: str
    message: str

RULES = [
    Rule(
        "idle-wait",
        re.compile(r"\bvk(Device|Queue)WaitIdle\s*\("),
        "high",
        "Idle wait found. Valid for teardown/simple recovery, but usually a frame-loop stall; prefer fences/timeline semaphores for normal flow.",
    ),
    Rule(
        "legacy-barrier",
        re.compile(r"\bvkCmdPipelineBarrier\s*\("),
        "medium",
        "Legacy barrier API found. For Vulkan 1.3, prefer synchronization2 (`vkCmdPipelineBarrier2`) unless this is a compatibility path.",
    ),
    Rule(
        "all-commands",
        re.compile(r"VK_PIPELINE_STAGE(_2)?_ALL_COMMANDS_BIT"),
        "medium",
        "Broad ALL_COMMANDS stage mask found. Check whether narrower producer/consumer stages are correct and faster.",
    ),
    Rule(
        "general-layout",
        re.compile(r"VK_IMAGE_LAYOUT_GENERAL"),
        "medium",
        "GENERAL layout found. It is sometimes required, but attachment/sample/transfer-specific layouts are usually preferable.",
    ),
    Rule(
        "per-resource-memory",
        re.compile(r"\bvkAllocateMemory\s*\("),
        "medium",
        "Raw memory allocation found. Ensure this is allocator setup/dedicated allocation, not per-resource allocation churn.",
    ),
    Rule(
        "descriptor-update",
        re.compile(r"\bvkUpdateDescriptorSets\s*\("),
        "info",
        "Descriptor update found. Check it is not in a per-draw hot path and lifetime is safe for in-flight GPU reads.",
    ),
    Rule(
        "pipeline-create",
        re.compile(r"\bvkCreate(Graphics|Compute|RayTracing|RayTracingPipelinesKHR|GraphicsPipelines|ComputePipelines)"),
        "info",
        "Pipeline creation found. Ensure pipeline creation is cached/warmed up and not unexpectedly in the frame loop.",
    ),
    Rule(
        "old-submit",
        re.compile(r"\bvkQueueSubmit\s*\("),
        "info",
        "Legacy submit found. For Vulkan 1.3 synchronization2 paths, consider `vkQueueSubmit2`.",
    ),
    Rule(
        "extension-name",
        re.compile(r"VK_[A-Z0-9_]+_EXTENSION_NAME"),
        "info",
        "Extension name reference found. Verify extension is enumerated, scope is correct, dependencies are met, and feature bits are enabled if required.",
    ),
]


def iter_files(root: Path) -> Iterable[Path]:
    if root.is_file():
        if root.suffix.lower() in SOURCE_EXTS:
            yield root
        return
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in {".git", "build", "cmake-build-debug", "cmake-build-release", "out", "third_party", "external"}]
        for filename in filenames:
            path = Path(dirpath) / filename
            if path.suffix.lower() in SOURCE_EXTS:
                yield path


def scan_file(path: Path) -> list[tuple[int, Rule, str]]:
    findings: list[tuple[int, Rule, str]] = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        print(f"warning: could not read {path}: {exc}")
        return findings
    for line_no, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("//"):
            continue
        for rule in RULES:
            if rule.pattern.search(line):
                findings.append((line_no, rule, stripped[:180]))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan C/C++ Vulkan code for common anti-patterns worth manual review.")
    parser.add_argument("paths", nargs="+", help="Files or directories to scan")
    parser.add_argument("--severity", choices=["info", "medium", "high"], default="info", help="Minimum severity to report")
    args = parser.parse_args()

    order = {"info": 0, "medium": 1, "high": 2}
    min_level = order[args.severity]
    total = 0

    for root_arg in args.paths:
        root = Path(root_arg)
        for path in iter_files(root):
            for line_no, rule, excerpt in scan_file(path):
                if order[rule.severity] < min_level:
                    continue
                total += 1
                print(f"{path}:{line_no}: {rule.severity}: {rule.name}: {rule.message}")
                print(f"    {excerpt}")

    print(f"\nfindings: {total}")
    if total:
        print("note: findings are review prompts, not proof of invalid Vulkan usage.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
