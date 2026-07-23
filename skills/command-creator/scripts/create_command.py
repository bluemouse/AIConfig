#!/usr/bin/env python3
"""
Create a portable slash command directly in the installed layout.

Example:
    python create_command.py \\
        --root /path/to/repo \\
        --name code-review \\
        --description "Review staged changes before commit." \\
        --body-file /tmp/code-review-body.md \\
        --overwrite
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from quick_validate import body_after_frontmatter, validate_command
from scaffold_command import (
    TOOL_PATHS,
    CommandCreatorError,
    build_claude_content,
    build_cursor_content,
    build_github_content,
    shared_command_content,
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

    shared_path = root / ".shared" / "commands" / f"{command_name}.md"
    shared_content = shared_command_content(command_name, description, body)

    shared_body = body_after_frontmatter(shared_content)
    cursor_content = build_cursor_content(shared_body)
    claude_content = build_claude_content(command_name, description, shared_body)
    github_content = build_github_content(command_name, description, shared_body)

    written: list[Path] = []
    for path, content in (
        (shared_path, shared_content),
        (root / TOOL_PATHS["cursor"].format(name=command_name), cursor_content),
        (root / TOOL_PATHS["claude"].format(name=command_name), claude_content),
        (root / TOOL_PATHS["github"].format(name=command_name), github_content),
    ):
        write_file(path, content, overwrite)
        written.append(path)

    return written


def validate_install(written: list[Path]) -> None:
    for path in written:
        valid, message = validate_command(path)
        if not valid:
            raise CommandCreatorError(f"Validation failed for {path}: {message}")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create portable command install outputs.")
    parser.add_argument("--root", required=True, help="Repository or output root directory.")
    parser.add_argument("--name", required=True, help="Command name; normalized to hyphen-case.")
    parser.add_argument("--description", required=True, help="Short command description.")
    parser.add_argument(
        "--body-file",
        required=True,
        help="Markdown file containing the tool-neutral command body (no frontmatter).",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing generated files if they already exist.",
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

    print("created command files:")
    for path in written:
        print(f"- {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
