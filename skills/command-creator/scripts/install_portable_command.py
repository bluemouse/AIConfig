#!/usr/bin/env python3
"""
Install a bootstrap command package as a portable command-skill.

Writes commands/<name>/COMMAND.md to .agents/skills/<name>/SKILL.md with
`disable-model-invocation: true`, so every coding agent exposes it as /<name>
and the model never self-invokes it. No tool-specific outputs are generated.

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
    BOOTSTRAP_COMMAND_FILENAME,
    COMMAND_SKILL_DIR_PARTS,
    COMMAND_SKILL_FILENAME,
    body_after_frontmatter,
    parse_frontmatter,
    validate_command_skill,
)
from scaffold_command import (
    CommandCreatorError,
    assert_command_skill_target_available,
    command_skill_content,
    slugify_name,
    write_file,
)


def read_command_metadata(command_md: Path) -> tuple[str, str, str, object | None]:
    if not command_md.is_file():
        raise CommandCreatorError(f"COMMAND.md not found in source: {command_md}")

    content = command_md.read_text(encoding="utf-8")
    frontmatter, error = parse_frontmatter(content)
    if error:
        raise CommandCreatorError(f"Invalid source COMMAND.md: {error}")

    # cr-012: reject non-strings rather than silently str()-coercing them
    # (a YAML list would become the literal "[a, b]" and can validate) —
    # mirrors read_agent_metadata in the agent-creator installer.
    description = frontmatter.get("description", "")
    if not isinstance(description, str):
        raise CommandCreatorError("Source COMMAND.md description must be a string.")
    if not description.strip():
        raise CommandCreatorError("Source COMMAND.md is missing a description in frontmatter.")

    source_name = frontmatter.get("name", "")
    if not isinstance(source_name, str):
        raise CommandCreatorError("Source COMMAND.md name must be a string.")
    body = body_after_frontmatter(content)
    if not body:
        raise CommandCreatorError("Source COMMAND.md body cannot be empty.")
    allowed_tools = frontmatter.get("allowed-tools")
    return description.strip(), source_name.strip(), body, allowed_tools


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

    command_md = source / BOOTSTRAP_COMMAND_FILENAME
    description, source_name, body, allowed_tools = read_command_metadata(command_md)
    if source_name and source_name != command_name:
        raise CommandCreatorError(
            f"Command name '{command_name}' does not match source frontmatter name '{source_name}'."
        )

    skill_dir = root.joinpath(*COMMAND_SKILL_DIR_PARTS) / command_name
    skill_path = skill_dir / COMMAND_SKILL_FILENAME

    assert_command_skill_target_available(skill_dir, skill_path, overwrite)

    content = command_skill_content(
        command_name,
        description,
        body,
        allowed_tools=allowed_tools,
    )
    write_file(skill_path, content, overwrite)

    return [skill_path]


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
        valid, message = validate_command_skill(path)
        if not valid:
            raise CommandCreatorError(f"Validation failed for {path}: {message}")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Install a bootstrap command as a portable command-skill."
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
        help="Overwrite an existing command-skill install (default: true).",
    )
    parser.add_argument(
        "--no-overwrite",
        action="store_false",
        dest="overwrite",
        help="Refuse to overwrite an existing command-skill install.",
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
        "\nRestart or reload the coding agent session so /"
        f"{slugify_name(args.name)} is rediscovered."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
