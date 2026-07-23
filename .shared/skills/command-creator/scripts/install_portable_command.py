#!/usr/bin/env python3
"""
Install a bootstrap command package into the portable shared-first layout.

Copies commands/<name>/COMMAND.md to .shared/commands/<name>.md and installs
tool-specific outputs for Cursor, Claude Code, and GitHub Copilot.

Example:
    python install_portable_command.py \\
        --root . \\
        --name code-review \\
        --source commands/code-review \\
        --overwrite
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from quick_validate import (
    body_after_frontmatter,
    parse_frontmatter,
    validate_command,
)
from scaffold_command import (
    SHARED_COMMAND_FILENAME,
    TOOL_PATHS,
    CommandCreatorError,
    build_claude_content,
    build_cursor_content,
    build_github_content,
    parse_wrapper_file,
    rebuild_frontmatter,
    slugify_name,
    write_file,
)


def read_command_metadata(command_md: Path) -> tuple[str, str, str]:
    if not command_md.is_file():
        raise CommandCreatorError(f"COMMAND.md not found in source: {command_md}")

    content = command_md.read_text(encoding="utf-8")
    frontmatter, error = parse_frontmatter(content)
    if error:
        raise CommandCreatorError(f"Invalid source COMMAND.md: {error}")

    description = str(frontmatter.get("description", "")).strip()
    if not description:
        raise CommandCreatorError("Source COMMAND.md is missing a description in frontmatter.")

    source_name = str(frontmatter.get("name", "")).strip()
    body = body_after_frontmatter(content)
    if not body:
        raise CommandCreatorError("Source COMMAND.md body cannot be empty.")
    return description, source_name, body


def sync_shared_description(content: str, description: str) -> str:
    frontmatter, error = parse_frontmatter(content)
    if error or not frontmatter:
        raise CommandCreatorError(f"Cannot sync description: {error or 'missing frontmatter'}")

    updated = dict(frontmatter)
    updated["description"] = description
    body = body_after_frontmatter(content)
    rebuilt = rebuild_frontmatter(updated)
    if body:
        rebuilt += "\n" + body + "\n"
    else:
        rebuilt += "\n"
    return rebuilt


def assert_install_allowed(target_paths: list[Path], overwrite: bool) -> None:
    if overwrite:
        return
    for path in target_paths:
        if path.exists():
            raise CommandCreatorError(f"Refusing to overwrite existing file: {path}")


def install_portable_command(
    root: Path,
    source: Path,
    command_name: str,
    overwrite: bool,
) -> list[Path]:
    root = root.resolve()
    source = source.resolve()
    command_name = slugify_name(command_name)

    if not source.is_dir():
        raise CommandCreatorError(f"Source directory not found: {source}")

    command_md = source / SHARED_COMMAND_FILENAME
    description, source_name, shared_body = read_command_metadata(command_md)
    if source_name and source_name != command_name:
        raise CommandCreatorError(
            f"Command name '{command_name}' does not match source frontmatter name '{source_name}'."
        )

    shared_path = root / ".shared" / "commands" / f"{command_name}.md"
    shared_content = sync_shared_description(command_md.read_text(encoding="utf-8"), description)

    cursor_path = root / TOOL_PATHS["cursor"].format(name=command_name)
    claude_path = root / TOOL_PATHS["claude"].format(name=command_name)
    github_path = root / TOOL_PATHS["github"].format(name=command_name)

    cursor_wrapper_path = source / "wrappers" / "cursor" / SHARED_COMMAND_FILENAME
    claude_wrapper_path = source / "wrappers" / "claude" / SHARED_COMMAND_FILENAME
    github_wrapper_path = source / "wrappers" / "github" / SHARED_COMMAND_FILENAME

    _, cursor_wrapper_body = parse_wrapper_file(cursor_wrapper_path, allow_frontmatter=False)
    claude_wrapper_fm, claude_wrapper_body = parse_wrapper_file(
        claude_wrapper_path, allow_frontmatter=True
    )
    github_wrapper_fm, github_wrapper_body = parse_wrapper_file(
        github_wrapper_path, allow_frontmatter=True
    )

    cursor_content = build_cursor_content(shared_body, cursor_wrapper_body)
    claude_content = build_claude_content(
        command_name,
        description,
        shared_body,
        claude_wrapper_body,
        claude_wrapper_fm,
    )
    github_content = build_github_content(
        command_name,
        description,
        shared_body,
        github_wrapper_body,
        github_wrapper_fm,
    )

    target_paths = [shared_path, cursor_path, claude_path, github_path]
    assert_install_allowed(target_paths, overwrite)

    write_file(shared_path, shared_content, overwrite)
    write_file(cursor_path, cursor_content, overwrite)
    write_file(claude_path, claude_content, overwrite)
    write_file(github_path, github_content, overwrite)

    return target_paths


def validate_bootstrap(source: Path, validator_script: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(validator_script), "--bootstrap-source", str(source)],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        detail = (result.stdout + result.stderr).strip() or "unknown error"
        raise CommandCreatorError(f"Bootstrap validation failed for {source}: {detail}")


def validate_install(written: list[Path]) -> None:
    for path in written:
        valid, message = validate_command(path)
        if not valid:
            raise CommandCreatorError(f"Validation failed for {path}: {message}")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Install a bootstrap command into the portable shared-first layout."
    )
    parser.add_argument("--root", required=True, help="Repository root directory.")
    parser.add_argument("--name", required=True, help="Command name; normalized to hyphen-case.")
    parser.add_argument(
        "--source",
        required=True,
        help="Path to the bootstrap command directory containing COMMAND.md.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        default=True,
        help="Overwrite existing shared command and tool outputs (default: true).",
    )
    parser.add_argument(
        "--no-overwrite",
        action="store_false",
        dest="overwrite",
        help="Refuse to overwrite existing install targets.",
    )
    parser.add_argument(
        "--skip-validate",
        action="store_true",
        help="Skip post-install validation (not recommended).",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    validator = Path(__file__).resolve().parent / "quick_validate.py"
    source = Path(args.source)

    try:
        validate_bootstrap(source, validator)
        written = install_portable_command(
            root=Path(args.root),
            source=source,
            command_name=args.name,
            overwrite=args.overwrite,
        )
    except CommandCreatorError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if not args.skip_validate:
        try:
            validate_install(written)
        except CommandCreatorError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1

    print(f"installed {slugify_name(args.name)}:")
    for path in written:
        print(f"- {path}")

    print(
        "\nReload Cursor, VS Code (Copilot), and Claude Code so each tool "
        "rediscovers the installed command."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
