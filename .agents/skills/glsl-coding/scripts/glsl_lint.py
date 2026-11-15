#!/usr/bin/env python3
"""Small static GLSL checklist for glsl-coding.

This is not a compiler. It flags common structural issues that are useful when
reviewing modern OpenGL/Vulkan GLSL shaders.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Tuple


@dataclass(frozen=True)
class Finding:
    path: Path
    line: int
    severity: str
    code: str
    message: str


def strip_block_comments_preserve_lines(text: str) -> str:
    def repl(match: re.Match[str]) -> str:
        return "\n" * match.group(0).count("\n")

    return re.sub(r"/\*.*?\*/", repl, text, flags=re.DOTALL)


def remove_line_comment(line: str) -> str:
    in_string = False
    i = 0
    while i + 1 < len(line):
        if line[i] == '"':
            in_string = not in_string
        if not in_string and line[i:i + 2] == "//":
            return line[:i]
        i += 1
    return line


def significant_lines(text: str) -> List[Tuple[int, str]]:
    no_blocks = strip_block_comments_preserve_lines(text)
    result: List[Tuple[int, str]] = []
    for idx, raw in enumerate(no_blocks.splitlines(), start=1):
        line = remove_line_comment(raw).strip()
        if line:
            result.append((idx, line))
    return result


def infer_stage(path: Path, text: str, requested: str) -> str:
    if requested != "auto":
        return requested
    name = path.name.lower()
    patterns = [
        ("tess-control", [".tesc", "tesc", "tess_control", "tesscontrol", ".tcs"]),
        ("tess-eval", [".tese", "tese", "tess_eval", "tesseval", ".tes", ".tesh", ".tesse", ".tesv", ".tese"]),
        ("vertex", [".vert", "vert", "vertex", ".vs", "_vs"]),
        ("fragment", [".frag", "frag", "fragment", "pixel", ".fs", "_fs", ".ps"]),
        ("geometry", [".geom", "geom", "geometry", ".gs", "_gs"]),
        ("compute", [".comp", "comp", "compute", ".cs", "_cs"]),
    ]
    for stage, keys in patterns:
        if any(k in name for k in keys):
            return stage
    if "local_size_" in text or "gl_GlobalInvocationID" in text:
        return "compute"
    if "gl_Position" in text:
        return "vertex"
    if "outColor" in text or "gl_FragColor" in text or "gl_FragCoord" in text:
        return "fragment"
    return "unknown"


def has_layout_binding(prefix: str) -> bool:
    return "layout" in prefix and "binding" in prefix


def check_file(path: Path, target: str, requested_stage: str) -> List[Finding]:
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = significant_lines(text)
    stage = infer_stage(path, text, requested_stage)
    findings: List[Finding] = []

    def add(line: int, severity: str, code: str, message: str) -> None:
        findings.append(Finding(path, line, severity, code, message))

    if not lines:
        add(1, "error", "empty", "shader file is empty")
        return findings

    first_line_no, first = lines[0]
    if not first.startswith("#version"):
        add(first_line_no, "error", "version-missing", "first significant line should be a #version directive")
    else:
        if target == "opengl" and "core" not in first and re.search(r"#version\s+(3[3-9]0|4[0-9]0)", first):
            add(first_line_no, "warning", "version-profile", "desktop OpenGL shaders should usually declare the core profile")

    deprecated = {
        r"\battribute\b": "use 'in' instead of legacy 'attribute'",
        r"\bvarying\b": "use explicit 'in'/'out' stage interfaces instead of legacy 'varying'",
        r"\bgl_FragColor\b": "declare an explicit fragment output, e.g. layout(location = 0) out vec4 outColor",
        r"\bgl_FragData\b": "declare explicit fragment outputs instead of gl_FragData",
        r"\btexture2D\s*\(": "use texture(...) instead of deprecated texture2D(...)",
        r"\btextureCube\s*\(": "use texture(...) instead of deprecated textureCube(...)",
        r"\bgl_TexCoord\b": "define your own varyings instead of gl_TexCoord",
        r"\bgl_MultiTexCoord": "define your own vertex attributes instead of gl_MultiTexCoord*",
        r"\bftransform\s*\(": "compute transforms explicitly instead of ftransform()",
    }
    for line_no, line in lines:
        for pattern, message in deprecated.items():
            if re.search(pattern, line):
                add(line_no, "warning", "legacy", message)

    if target in ("vulkan", "auto"):
        for line_no, line in lines:
            normalized = " ".join(line.split())
            if re.search(r"\buniform\s+(sampler|[iu]?sampler|texture|[iu]?texture|image|[iu]?image|subpassInput)", normalized):
                before_uniform = normalized.split("uniform", 1)[0]
                if "binding" not in before_uniform:
                    add(line_no, "warning", "vk-binding", "Vulkan descriptor resources should have explicit layout(set = M, binding = N)")
                elif "set" not in before_uniform:
                    add(line_no, "info", "vk-set", "prefer an explicit descriptor set as well as binding for Vulkan resources")
            if re.search(r"^uniform\s+(bool|int|uint|float|double|[biud]?vec[234]|mat[234])\b", normalized):
                add(line_no, "warning", "vk-default-uniform", "Vulkan GLSL should use uniform blocks, push constants, specialization constants, or descriptors instead of default uniforms")
            if re.search(r"\bgl_VertexID\b", normalized):
                add(line_no, "warning", "vk-builtin", "Vulkan GLSL uses gl_VertexIndex rather than OpenGL gl_VertexID")
            if re.search(r"\bgl_InstanceID\b", normalized):
                add(line_no, "warning", "vk-builtin", "Vulkan GLSL uses gl_InstanceIndex rather than OpenGL gl_InstanceID")

    if stage == "vertex" and "gl_Position" not in text:
        add(1, "warning", "vertex-position", "vertex-like shader does not write gl_Position")

    if stage == "fragment":
        has_explicit_output = any(re.search(r"\blayout\s*\([^)]*location\s*=\s*\d+[^)]*\)\s*out\b", line) for _, line in lines)
        if not has_explicit_output and "gl_FragColor" not in text and "gl_FragData" not in text:
            add(1, "warning", "fragment-output", "fragment shader should declare an explicit layout(location = N) output")
        if re.search(r"\bdiscard\b", text):
            add(1, "info", "discard", "discard may affect early depth/stencil optimizations; keep it before expensive work when possible")
        if "gl_FragDepth" in text:
            add(1, "info", "frag-depth", "writing gl_FragDepth can limit early depth optimization; verify it is needed")

    if stage == "compute":
        if not re.search(r"layout\s*\([^)]*local_size_x", text):
            add(1, "error", "compute-local-size", "compute shader must declare local_size_x/y/z layout")
        if re.search(r"\bimageStore\s*\(|\bbuffer\b", text):
            add(1, "info", "host-barrier", "shader writes require appropriate API memory/pipeline barriers before later reads")

    for line_no, line in lines:
        if re.search(r"\bfor\s*\(", line) and not re.search(r"\+\+|--", line):
            add(line_no, "info", "loop", "review loop bounds and termination for GPU-friendliness")

    return findings


def format_findings(findings: Sequence[Finding]) -> str:
    if not findings:
        return "no static GLSL checklist findings"
    return "\n".join(
        f"{f.path}:{f.line}: {f.severity}: {f.code}: {f.message}"
        for f in findings
    )


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Static GLSL checklist for common modern OpenGL/Vulkan issues.")
    parser.add_argument("files", nargs="+", type=Path, help="GLSL shader files to inspect")
    parser.add_argument("--target", choices=["auto", "opengl", "vulkan"], default="auto", help="shader API target")
    parser.add_argument("--stage", choices=["auto", "vertex", "fragment", "tess-control", "tess-eval", "geometry", "compute"], default="auto", help="shader stage")
    args = parser.parse_args(argv)

    all_findings: List[Finding] = []
    had_read_error = False
    for path in args.files:
        if not path.exists():
            print(f"{path}:0: error: file-not-found: file does not exist", file=sys.stderr)
            had_read_error = True
            continue
        try:
            all_findings.extend(check_file(path, args.target, args.stage))
        except OSError as exc:
            print(f"{path}:0: error: read-failed: {exc}", file=sys.stderr)
            had_read_error = True

    print(format_findings(all_findings))
    if had_read_error or any(f.severity == "error" for f in all_findings):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
