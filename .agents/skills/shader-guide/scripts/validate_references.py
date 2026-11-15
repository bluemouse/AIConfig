#!/usr/bin/env python3
"""Validate shader-guide reference markdown for migration defects."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Issue:
    path: Path
    line: int
    code: str
    message: str


ORPHAN_BULLET = re.compile(r"^- \*\*\s*$")
TITLE_ONLY_STEP = re.compile(r"^\d+\. \*\*Step \d+:[^—]*$")
TRUNCATION_PATTERNS = [
    (re.compile(r"pass in$"), "truncated-line"),
    (re.compile(r"concept in$"), "truncated-line"),
    (re.compile(r"and the -"), "truncated-line"),
    (re.compile(r"Establish the standard$"), "truncated-line"),
]
LEGACY_TOKENS = ("iResolution", "mainImage", "ShaderToy", "WebGL")
ALLOWED_LEGACY_FILE = "source-map.md"


def validate_file(path: Path) -> list[Issue]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    issues: list[Issue] = []
    in_how_to_apply = False

    for idx, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped == "## How to Apply":
            in_how_to_apply = True
            continue
        if stripped.startswith("## ") and in_how_to_apply:
            in_how_to_apply = False

        if ORPHAN_BULLET.match(stripped):
            issues.append(Issue(path, idx, "orphan-bullet", "orphan bullet '- **'"))
            continue

        for pattern, code in TRUNCATION_PATTERNS:
            if pattern.search(line):
                issues.append(Issue(path, idx, code, f"truncation marker matched: {pattern.pattern}"))
                break

        if "gl_FragCoord.xy.xy" in line:
            issues.append(Issue(path, idx, "invalid-coord", "gl_FragCoord.xy.xy should be gl_FragCoord.xy"))

        if path.name != ALLOWED_LEGACY_FILE:
            for token in LEGACY_TOKENS:
                if token in line:
                    issues.append(
                        Issue(
                            path,
                            idx,
                            "legacy-token",
                            f"legacy token '{token}' only allowed in {ALLOWED_LEGACY_FILE}",
                        )
                    )
                    break

        if in_how_to_apply and TITLE_ONLY_STEP.match(stripped):
            issues.append(Issue(path, idx, "title-only-step", "How to Apply step lacks prose summary after em dash"))

    return issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate shader-guide reference markdown.")
    parser.add_argument(
        "references_dir",
        nargs="?",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "references",
        help="Path to references/ directory (default: sibling of scripts/)",
    )
    args = parser.parse_args(argv)

    ref_dir = args.references_dir.resolve()
    if not ref_dir.is_dir():
        print(f"error: not a directory: {ref_dir}", file=sys.stderr)
        return 1

    all_issues: list[Issue] = []
    for path in sorted(ref_dir.glob("*.md")):
        all_issues.extend(validate_file(path))

    if not all_issues:
        print(f"OK: {ref_dir} ({len(list(ref_dir.glob('*.md')))} files)")
        return 0

    for issue in all_issues:
        print(f"{issue.path}:{issue.line}: {issue.code}: {issue.message}")
    print(f"\n{len(all_issues)} issue(s) in {ref_dir}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
