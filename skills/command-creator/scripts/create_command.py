#!/usr/bin/env python3
"""
Create a portable command-skill directly in the installed layout.

Example:
    python create_command.py \\
        --root /path/to/repo \\
        --name code-review \\
        --description "Review staged changes when the user explicitly invokes /code-review." \\
        --body-file /tmp/code-review-body.md \\
        --overwrite
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from quick_validate import (
    COMMAND_SKILL_DIR_PARTS,
    COMMAND_SKILL_FILENAME,
    command_skill_dir_name,
    validate_command_skill,
)
from scaffold_command import (
    CommandCreatorError,
    assert_command_skill_target_available,
    command_skill_content,
    slugify_name,
    write_file,
)


def create_command(
    root: Path,
    name: str,
    description: str,
    body: str,
    overwrite: bool,
) -> list[Path]:
    root = root.resolve()
    command_name = slugify_name(name)
    if not description.strip():
        raise CommandCreatorError("Description cannot be empty.")

    # Install dir = cmd- prefix + command name; the slash command stays
    # /<name> (frontmatter name is the invocation identity).
    skill_dir = root.joinpath(*COMMAND_SKILL_DIR_PARTS) / command_skill_dir_name(command_name)
    skill_path = skill_dir / COMMAND_SKILL_FILENAME

    assert_command_skill_target_available(skill_dir, skill_path, overwrite)

    content = command_skill_content(command_name, description, body)
    write_file(skill_path, content, overwrite)

    return [skill_path]


def validate_install(written: list[Path]) -> None:
    for path in written:
        valid, message = validate_command_skill(path)
        if not valid:
            raise CommandCreatorError(f"Validation failed for {path}: {message}")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a portable command-skill.")
    parser.add_argument("--root", required=True, help="Repository or output root directory.")
    parser.add_argument("--name", required=True, help="Command name; normalized to hyphen-case.")
    parser.add_argument("--description", required=True, help="Short command description.")
    parser.add_argument(
        "--body-file",
        required=True,
        help="Markdown file containing the command body (no frontmatter).",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite an existing command-skill install if it already exists.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        body_path = Path(args.body_file)
        if not body_path.exists():
            raise CommandCreatorError(f"Body file not found: {body_path}")
        body = body_path.read_text(encoding="utf-8")
        written = create_command(
            root=Path(args.root),
            name=args.name,
            description=args.description,
            body=body,
            overwrite=args.overwrite,
        )
    except CommandCreatorError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    try:
        validate_install(written)
    except CommandCreatorError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print("created command skill:")
    for path in written:
        print(f"- {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
