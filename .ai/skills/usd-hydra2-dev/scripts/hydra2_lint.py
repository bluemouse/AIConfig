#!/usr/bin/env python3
"""
Lightweight Hydra 2.0 snippet checker.

This script flags common mistakes in AI-generated OpenUSD Hydra 2.0 C++.
It is not a compiler and does not verify APIs against a checkout. Use it as a
pre-review aid before source verification and compilation.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Iterable, List, Tuple

Warning = Tuple[str, str]

ABSTRACT_DATASOURCE_NEW_RE = re.compile(
    r"\bHd(?:Bool|Token|Int|UInt|Float|Double|Matrix|Vec[234][fdih]|Path|String|"
    r"[A-Za-z0-9]+Array)DataSource\s*::\s*New\s*\("
)

IGNORE_BLOCK_RE = re.compile(
    r"<!--\s*hydra2-lint:\s*ignore-start\s*-->.*?<!--\s*hydra2-lint:\s*ignore-end\s*-->",
    re.DOTALL,
)

TRAP_LINE_RE = re.compile(
    r"^\s*[-*]\s+`?Hd(?:TokenDataSource|DataSourceSentinelTokens)",
    re.MULTILINE,
)


def _strip_ignored_regions(text: str) -> str:
    return IGNORE_BLOCK_RE.sub("", text)


def _line_for_offset(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def check_text(text: str) -> List[Warning]:
    warnings: List[Warning] = []
    lint_text = _strip_ignored_regions(text)

    for m in ABSTRACT_DATASOURCE_NEW_RE.finditer(lint_text):
        line = _line_for_offset(lint_text, m.start())
        if TRAP_LINE_RE.search(lint_text):
            # Allow abstract datasource names in trap-list bullets.
            line_start = lint_text.rfind("\n", 0, m.start()) + 1
            line_end = lint_text.find("\n", m.start())
            if line_end == -1:
                line_end = len(lint_text)
            if line_start == 0 or lint_text[line_start - 1] == "\n":
                line_content = lint_text[line_start:line_end]
                if TRAP_LINE_RE.match(line_content) or line_content.strip().startswith("- `Hd"):
                    continue
        warnings.append((
            str(line),
            "possible abstract datasource ::New call; prefer HdRetainedTypedSampledDataSource<T>::New(...) unless source proves this class is concrete",
        ))

    if "HdDataSourceSentinelTokens" in lint_text and "HdDataSourceLocatorSentinelTokens" not in lint_text:
        warnings.append((
            "global",
            "uses HdDataSourceSentinelTokens without HdDataSourceLocatorSentinelTokens; prefer HdDataSourceLocatorSentinelTokens->container",
        ))
    elif "HdDataSourceSentinelTokens" in lint_text:
        # Mentioned alongside the correct token — likely documentation of the trap.
        if "legacy" not in lint_text.lower() and "wrong" not in lint_text.lower() and "do not" not in lint_text.lower():
            warnings.append((
                "global",
                "mentions HdDataSourceSentinelTokens; verify this is intentional legacy documentation, not usage",
            ))

    if "HdContainerDataSourceEditor" in lint_text and ".Finish()" in lint_text and "ComputeDirtyLocators" not in lint_text:
        warnings.append((
            "global",
            "uses HdContainerDataSourceEditor::Finish() without ComputeDirtyLocators; verify container-handle dirtying for runtime updates",
        ))

    if "PrimsDirtied" in lint_text and "UniversalSet" in lint_text:
        warnings.append((
            "global",
            "uses UniversalSet for dirtying; verify this broad invalidation is intentional and not an avoidable performance cost",
        ))

    if "class " in lint_text and "HdSingleInputFilteringSceneIndexBase" in lint_text:
        for hook in ["_PrimsAdded", "_PrimsRemoved", "_PrimsDirtied"]:
            if hook not in lint_text:
                warnings.append((
                    "global",
                    f"filtering scene index appears to omit {hook}; verify observer forwarding/translation is implemented",
                ))

    if "_SendPrimsDirtied" in lint_text and "HdDataSourceLocatorSet" not in lint_text:
        warnings.append((
            "global",
            "sends dirty notices but no HdDataSourceLocatorSet appears in the snippet; verify precise dirty locators are authored",
        ))

    if "displayOpacity" in lint_text and "opacity" not in lint_text and "material" not in lint_text:
        warnings.append((
            "global",
            "displayOpacity appears without material opacity; verify whether masked/cutout behavior is intended rather than true semitransparency",
        ))

    if "GetPrim" in lint_text and "GetChildPrimPaths" not in lint_text:
        warnings.append((
            "global",
            "GetPrim appears without GetChildPrimPaths; verify traversal/existence consistency in the full class",
        ))

    legacy_hits = [
        token for token in ("HdRenderDelegate", "HdSceneDelegate", "HdRenderIndex")
        if token in lint_text
    ]
    if legacy_hits:
        legacy_doc = any(
            phrase in lint_text
            for phrase in (
                "legacy Hydra 1.0",
                "compatibility",
                "migrating",
                "emulation",
                "bridge",
                "replaced by",
            )
        )
        if not legacy_doc:
            warnings.append((
                "global",
                "legacy Hydra 1.0 API appears; verify this is intentional compatibility code and not new Hydra 2.0 design",
            ))

    return warnings


def iter_inputs(paths: Iterable[str]) -> Iterable[Tuple[str, str]]:
    any_path = False
    for raw in paths:
        any_path = True
        path = Path(raw)
        try:
            yield str(path), path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            yield str(path), path.read_text(encoding="utf-8", errors="replace")
    if not any_path:
        yield "<stdin>", sys.stdin.read()


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="check Hydra 2.0 C++ snippets for common mistakes")
    parser.add_argument("paths", nargs="*", help="files to check; reads stdin when omitted")
    args = parser.parse_args(argv)

    exit_code = 0
    for label, text in iter_inputs(args.paths):
        warnings = check_text(text)
        if warnings:
            exit_code = 1
            print(f"{label}:")
            for loc, message in warnings:
                print(f"  warning:{loc}: {message}")
        else:
            print(f"{label}: no hydra2-lint warnings")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
