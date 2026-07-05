#!/usr/bin/env python3
"""Run or print a Slang compile matrix for Vulkan SPIR-V and Metal MSL.

Manifest example:
{
  "slangc": "slangc",
  "source": "shaders/main.slang",
  "out_dir": "build/shaders",
  "profile": "glsl_460",
  "entries": [
    {"name": "vertexMain", "stage": "vertex"},
    {"name": "fragmentMain", "stage": "fragment"},
    {"name": "computeMain", "stage": "compute"}
  ],
  "targets": ["vulkan", "metal"],
  "extra_args": ["-Wall"]
}
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

TARGETS = {
    "vulkan": {"slang_target": "spirv", "ext": ".spv"},
    "vulkan-asm": {"slang_target": "spirv-asm", "ext": ".spvasm"},
    "metal": {"slang_target": "metal", "ext": ".metal"},
}


def load_manifest(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as exc:  # pragma: no cover - CLI error path
        raise SystemExit(f"failed to read manifest {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise SystemExit("manifest must be a JSON object")
    return data


def require_str(data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value:
        raise SystemExit(f"manifest field '{key}' must be a non-empty string")
    return value


def build_commands(data: dict[str, Any]) -> list[list[str]]:
    slangc = data.get("slangc", "slangc")
    if not isinstance(slangc, str) or not slangc:
        raise SystemExit("manifest field 'slangc' must be a non-empty string when provided")

    source = require_str(data, "source")
    out_dir = Path(data.get("out_dir", "build/slang"))
    profile = data.get("profile")
    if profile is not None and not isinstance(profile, str):
        raise SystemExit("manifest field 'profile' must be a string when provided")

    entries = data.get("entries")
    if not isinstance(entries, list) or not entries:
        raise SystemExit("manifest field 'entries' must be a non-empty array")

    targets = data.get("targets", ["vulkan", "metal"])
    if not isinstance(targets, list) or not targets:
        raise SystemExit("manifest field 'targets' must be a non-empty array")
    for target in targets:
        if target not in TARGETS:
            raise SystemExit(f"unsupported target '{target}', expected one of {sorted(TARGETS)}")

    extra_args = data.get("extra_args", [])
    if not isinstance(extra_args, list) or not all(isinstance(x, str) for x in extra_args):
        raise SystemExit("manifest field 'extra_args' must be an array of strings")

    commands: list[list[str]] = []
    for entry in entries:
        if not isinstance(entry, dict):
            raise SystemExit("each entry must be an object with name and stage")
        name = entry.get("name")
        stage = entry.get("stage")
        if not isinstance(name, str) or not name:
            raise SystemExit("each entry requires a non-empty string 'name'")
        if stage not in {"vertex", "fragment", "compute"}:
            raise SystemExit("each entry stage must be one of: vertex, fragment, compute")
        for target in targets:
            target_info = TARGETS[target]
            out = out_dir / target / f"{name}{target_info['ext']}"
            cmd = [
                slangc,
                source,
                "-entry",
                name,
                "-stage",
                stage,
                "-target",
                target_info["slang_target"],
            ]
            if profile and target.startswith("vulkan"):
                cmd += ["-profile", profile]
            cmd += ["-o", str(out)]
            cmd += extra_args
            commands.append(cmd)
    return commands


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path, help="path to JSON compile manifest")
    parser.add_argument("--print-only", action="store_true", help="print commands without running them")
    parser.add_argument("--allow-missing-slangc", action="store_true", help="print commands and exit 0 if slangc is not found")
    args = parser.parse_args(argv)

    data = load_manifest(args.manifest)
    commands = build_commands(data)

    slangc = commands[0][0] if commands else "slangc"
    if shutil.which(slangc) is None:
        for cmd in commands:
            print(" ".join(cmd))
        if args.print_only or args.allow_missing_slangc:
            print(f"note: '{slangc}' was not found; commands were not executed", file=sys.stderr)
            return 0
        print(f"error: '{slangc}' was not found", file=sys.stderr)
        return 127

    for cmd in commands:
        print(" ".join(cmd))
        if args.print_only:
            continue
        out_path = Path(cmd[cmd.index("-o") + 1])
        out_path.parent.mkdir(parents=True, exist_ok=True)
        completed = subprocess.run(cmd, text=True)
        if completed.returncode != 0:
            return completed.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
