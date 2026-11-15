#!/usr/bin/env python3
"""
Create a skill in the single-root .agents/skills/ layout.

Example:
    python create_skill.py --root /path/to/repo --name my-skill --overwrite
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from scaffold_skill import SkillScaffoldError, scaffold_portable_skill, slugify_name


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a skill scaffold in the single-root .agents/skills/ layout."
    )
    parser.add_argument("--root", required=True, help="Repository or output root directory.")
    parser.add_argument("--name", required=True, help="Skill name; normalized to hyphen-case.")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing generated files if they already exist.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        skill_name = slugify_name(args.name)
        written = scaffold_portable_skill(
            root=Path(args.root),
            skill_name=skill_name,
            overwrite=args.overwrite,
        )
    except SkillScaffoldError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print("created skill files:")
    for path in written:
        if path.is_dir():
            print(f"- {path}/")
        else:
            print(f"- {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
