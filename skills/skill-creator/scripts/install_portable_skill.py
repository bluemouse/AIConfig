#!/usr/bin/env python3
"""
Install a bootstrap skill package into the portable shared-first layout.

Copies a source skill directory to .shared/skills/<name>/ and generates
tool wrappers for Claude Code, Cursor, and GitHub Copilot.

Example:
    python install_portable_skill.py \\
        --root . \\
        --name skill-creator \\
        --source skills/skill-creator \\
        --overwrite
"""

from __future__ import annotations

import argparse
import fnmatch
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

from quick_validate import body_after_frontmatter, parse_frontmatter, validate_skill
from scaffold_skill import (
    TOOL_SKILL_PATHS,
    SkillScaffoldError,
    slugify_name,
    wrapper_skill_content,
    write_file,
)

DEFAULT_TOOL_NOTES = {
    "cursor": (
        "Reload the Cursor window after adding or editing this skill "
        "so the agent rediscovers it."
    ),
    "claude": (
        "Restart or reload the Claude Code session after adding or editing "
        "this skill so the agent rediscovers it."
    ),
    "github": (
        "Reload VS Code after adding or editing this skill so Copilot "
        "rediscovers it."
    ),
}

IGNORE_DIR_NAMES = {"__pycache__"}
IGNORE_FILE_GLOBS = ("*.pyc", "*.skill")


def should_ignore(name: str) -> bool:
    if name in IGNORE_DIR_NAMES:
        return True
    return any(fnmatch.fnmatch(name, pattern) for pattern in IGNORE_FILE_GLOBS)


def make_copy_ignore(source: Path):
    """Return shutil ignore callback; omit bootstrap-only wrappers/ from shared copy."""
    source_resolved = source.resolve()

    def ignore(directory: str, names: list[str]) -> list[str]:
        ignored = [name for name in names if should_ignore(name)]
        if Path(directory).resolve() == source_resolved and "wrappers" in names:
            ignored.append("wrappers")
        return ignored

    return ignore


def copy_skill_source(source: Path, dest: Path, overwrite: bool) -> None:
    if dest.exists():
        if not overwrite:
            raise SkillScaffoldError(
                f"Refusing to overwrite existing directory: {dest}"
            )
        shutil.rmtree(dest)

    shutil.copytree(source, dest, ignore=make_copy_ignore(source))


def read_skill_description(skill_md: Path) -> tuple[str, str]:
    if not skill_md.is_file():
        raise SkillScaffoldError(f"SKILL.md not found in source: {skill_md}")

    frontmatter, error = parse_frontmatter(skill_md.read_text(encoding="utf-8"))
    if error:
        raise SkillScaffoldError(f"Invalid source SKILL.md: {error}")

    description = frontmatter.get("description", "").strip()
    if not description:
        raise SkillScaffoldError("Source SKILL.md is missing a description in frontmatter.")

    source_name = frontmatter.get("name", "").strip()
    return description, source_name


def sync_description(content: str, description: str) -> str:
    fm, error = parse_frontmatter(content)
    if error or not fm:
        raise SkillScaffoldError(
            f"Cannot sync description: {error or 'missing frontmatter'}"
        )

    name = fm.get("name", "").strip()
    if not name:
        raise SkillScaffoldError("Wrapper is missing name in frontmatter")

    updated = dict(fm)
    updated["description"] = description
    body = body_after_frontmatter(content)
    yaml_block = yaml.dump(
        updated,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False,
    ).strip()
    rebuilt = f"---\n{yaml_block}\n---\n"
    if body:
        rebuilt += "\n" + body + "\n"
    else:
        rebuilt += "\n"
    return rebuilt


def wrapper_with_description(
    tool: str,
    skill_name: str,
    note: str,
    description: str,
) -> str:
    content = wrapper_skill_content(tool, skill_name, note)
    return sync_description(content, description)


def load_custom_wrapper(source: Path, tool: str, description: str) -> str | None:
    wrapper_path = source / "wrappers" / tool / "SKILL.md"
    if not wrapper_path.is_file():
        return None
    return sync_description(wrapper_path.read_text(encoding="utf-8"), description)


def install_portable_skill(
    root: Path,
    source: Path,
    skill_name: str,
    overwrite: bool,
    claude_note: str | None = None,
    cursor_note: str | None = None,
    github_note: str | None = None,
) -> list[Path]:
    root = root.resolve()
    source = source.resolve()
    skill_name = slugify_name(skill_name)

    if not source.is_dir():
        raise SkillScaffoldError(f"Source directory not found: {source}")

    description, source_name = read_skill_description(source / "SKILL.md")
    if source_name and source_name != skill_name:
        raise SkillScaffoldError(
            f"Skill name '{skill_name}' does not match source frontmatter name '{source_name}'."
        )

    shared_dir = root / ".shared" / "skills" / skill_name
    copy_skill_source(source, shared_dir, overwrite)

    notes = {
        "claude": claude_note or DEFAULT_TOOL_NOTES["claude"],
        "cursor": cursor_note or DEFAULT_TOOL_NOTES["cursor"],
        "github": github_note or DEFAULT_TOOL_NOTES["github"],
    }

    written: list[Path] = [shared_dir]
    for tool, pattern in TOOL_SKILL_PATHS.items():
        wrapper_dir = root / pattern.format(name=skill_name)
        content = load_custom_wrapper(source, tool, description)
        if content is None:
            content = wrapper_with_description(
                tool,
                skill_name,
                notes[tool],
                description,
            )
        write_file(wrapper_dir / "SKILL.md", content, overwrite=True)
        written.append(wrapper_dir)

    return written


def validate_install(root: Path, skill_name: str, validator_script: Path) -> None:
    paths = [
        root / ".shared" / "skills" / skill_name,
        root / ".cursor" / "skills" / skill_name,
        root / ".claude" / "skills" / skill_name,
        root / ".github" / "skills" / skill_name,
    ]
    for path in paths:
        valid, message = validate_skill(path)
        if not valid:
            raise SkillScaffoldError(f"Validation failed for {path}: {message}")

        result = subprocess.run(
            [sys.executable, str(validator_script), str(path)],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            detail = (result.stdout + result.stderr).strip() or "unknown error"
            raise SkillScaffoldError(f"Validation failed for {path}: {detail}")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Install a bootstrap skill into the portable shared-first layout."
    )
    parser.add_argument("--root", required=True, help="Repository root directory.")
    parser.add_argument("--name", required=True, help="Skill name; normalized to hyphen-case.")
    parser.add_argument(
        "--source",
        required=True,
        help="Path to the bootstrap skill directory to copy into .shared/skills/.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        default=True,
        help="Overwrite existing shared skill and wrappers (default: true).",
    )
    parser.add_argument(
        "--no-overwrite",
        action="store_false",
        dest="overwrite",
        help="Refuse to overwrite existing install targets.",
    )
    parser.add_argument("--claude-note", help="Extra Claude Code-specific wrapper note.")
    parser.add_argument("--cursor-note", help="Extra Cursor-specific wrapper note.")
    parser.add_argument("--github-note", help="Extra GitHub Copilot-specific wrapper note.")
    parser.add_argument(
        "--skip-validate",
        action="store_true",
        help="Skip post-install validation (not recommended).",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        written = install_portable_skill(
            root=Path(args.root),
            source=Path(args.source),
            skill_name=args.name,
            overwrite=args.overwrite,
            claude_note=args.claude_note,
            cursor_note=args.cursor_note,
            github_note=args.github_note,
        )
    except SkillScaffoldError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if not args.skip_validate:
        validator = Path(__file__).resolve().parent / "quick_validate.py"
        try:
            validate_install(Path(args.root), slugify_name(args.name), validator)
        except SkillScaffoldError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1

    print(f"installed {slugify_name(args.name)}:")
    for path in written:
        if path.is_dir():
            print(f"- {path}/")
        else:
            print(f"- {path}")

    print(
        "\nReload Cursor, VS Code (Copilot), and Claude Code so each tool "
        "rediscovers the installed skill."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
