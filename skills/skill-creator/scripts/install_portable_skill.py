#!/usr/bin/env python3
"""
Install a bootstrap skill package into the single-root portable layout.

Copies a source skill directory to .agents/skills/<name>/ and creates the
Claude Code bridge symlink .claude/skills -> ../.agents/skills so Claude
Code discovers the installed skill. Other tools read .agents/skills/
directly.

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
import os
import shutil
import subprocess
import sys
from pathlib import Path

from quick_validate import parse_frontmatter, validate_skill
from scaffold_skill import SkillScaffoldError, slugify_name

# cr-010: this path constant is re-declared by sibling modules (bootstrap
# layout mandates independent script dirs) — tools/installer.py
# (SHARED_SKILL_DIR) and skills/command-creator/scripts/quick_validate.py
# (COMMAND_SKILL_DIR_PARTS) declare the same .agents/skills/ root; change
# them together.
SHARED_SKILL_DIR = ".agents/skills/{name}"
BRIDGE_LINK = ".claude/skills"
BRIDGE_TARGET = "../.agents/skills"

IGNORE_DIR_NAMES = {
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    ".hypothesis",
    "node_modules",
    "testdata",
    "fixtures",
    "evals",
}
IGNORE_FILE_GLOBS = (
    "*.pyc",
    "*.pyo",
    "*.skill",
    ".DS_Store",
    ".coverage",
    ".coverage.*",
    "eval-queries.json",
    "SOURCES.md",
    "conftest.py",
    "test_*.py",
    "*_test.py",
)


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


def ensure_bridge_symlink(root: Path) -> bool:
    """Bridge ``<root>/.claude/skills`` to ``../.agents/skills`` for Claude Code.

    Returns True when the bridge exists (pre-existing or newly created).
    Raises SkillScaffoldError when ``.claude/skills`` is a real directory;
    warns and returns False when the bridge cannot be created (symlink
    failure, or ``.claude`` exists as something other than a directory —
    e.g. a regular file, cr-007).
    """
    bridge = root / BRIDGE_LINK

    if bridge.is_symlink():
        if os.readlink(bridge) == BRIDGE_TARGET:
            return True
        print(
            f"warning: {bridge} is a symlink to {os.readlink(bridge)}, "
            f"expected {BRIDGE_TARGET}; leaving it as-is",
            file=sys.stderr,
        )
        return False

    if bridge.exists():
        raise SkillScaffoldError(
            f"Refusing to replace existing real directory {bridge} with the "
            f"bridge symlink ({BRIDGE_TARGET}). Purge the legacy install "
            f"first (remove {bridge}), then re-run the install."
        )

    try:
        # cr-007: a regular file at <root>/.claude makes this mkdir raise
        # FileExistsError (an OSError) — handled with the same warning +
        # return False as a symlink-creation failure, never a raw traceback.
        bridge.parent.mkdir(parents=True, exist_ok=True)
        os.symlink(BRIDGE_TARGET, bridge)
    except OSError as exc:
        print(
            f"warning: could not create Claude Code bridge symlink {bridge} "
            f"({exc}); skipping — Claude Code will not discover .agents/skills/ "
            "until the bridge exists",
            file=sys.stderr,
        )
        return False
    return True


def verify_source_skill(source: Path, skill_name: str) -> None:
    # Flat-root rule (matches quick_validate): the source skill directory must
    # be a direct child of a directory named "skills" — category subfolders
    # (e.g. skills/category/<name>) are rejected.
    if source.parent.name != "skills":
        raise SkillScaffoldError(
            f"Skill source '{source}' must be a direct child of a skills root "
            f"(a directory named 'skills'), not nested in a category folder. "
            f"Move the skill to '<skills-root>/{skill_name}/'."
        )

    skill_md = source / "SKILL.md"
    if not skill_md.is_file():
        raise SkillScaffoldError(f"SKILL.md not found in source: {skill_md}")

    frontmatter, error = parse_frontmatter(skill_md.read_text(encoding="utf-8"))
    if error:
        raise SkillScaffoldError(f"Invalid source SKILL.md: {error}")

    description = frontmatter.get("description", "").strip()
    if not description:
        raise SkillScaffoldError("Source SKILL.md is missing a description in frontmatter.")

    source_name = frontmatter.get("name", "").strip()
    if source_name and source_name != skill_name:
        raise SkillScaffoldError(
            f"Skill name '{skill_name}' does not match source frontmatter name '{source_name}'."
        )


def is_command_skill(skill_md: Path) -> bool:
    """True when the SKILL.md at this path was installed as a command-skill.

    Twin sites (cr-010 — bootstrap layout mandates independent script dirs,
    so this is re-implemented locally; keep the flag semantics identical):
    skills/command-creator/scripts/scaffold_command.py:is_command_skill and
    tools/installer.py:is_command_skill.
    """
    if not skill_md.is_file():
        return False
    try:
        content = skill_md.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        # cr-102: unreadable reads as a plain skill, never a traceback —
        # same semantics as the tools twin (installer.py:is_command_skill).
        return False
    frontmatter, error = parse_frontmatter(content)
    if error or not frontmatter:
        return False
    return frontmatter.get("disable-model-invocation") is True


def assert_not_replacing_command_skill(source: Path, dest: Path) -> None:
    """Refuse a plain-skill install over an existing command-skill (cr-004).

    Commands and skills share .agents/skills/; overwriting a command-skill
    with a plain skill would silently drop ``disable-model-invocation: true``
    and convert a slash-command into a model-invocable skill. Refused even
    under --overwrite, before any bridge/copy write. The reverse direction
    (command over plain skill) is guarded by
    scaffold_command.assert_command_skill_target_available.
    """
    dest_skill_md = dest / "SKILL.md"
    source_skill_md = source / "SKILL.md"
    if is_command_skill(dest_skill_md) and not is_command_skill(source_skill_md):
        raise SkillScaffoldError(
            f"Refusing to overwrite command-skill {dest_skill_md} with a "
            "plain skill: commands and skills share .agents/skills/, and the "
            "copy would drop disable-model-invocation: true (converting a "
            "slash-command into a model-invocable skill). Remove it with the "
            "command installer's uninstall, or pick a different skill name."
        )


def install_portable_skill(
    root: Path,
    source: Path,
    skill_name: str,
    overwrite: bool,
) -> list[Path]:
    """Copy a source skill into .agents/skills/ and bridge Claude Code to it.

    Ordering note (cr-013, documented-not-reordered): the bridge is created
    before the overwrite check, so a refused --no-overwrite install may still
    leave the bridge behind. Benign — the bridge points at the existing
    install and is what a later successful install would create anyway.
    """
    root = root.resolve()
    source = source.resolve()
    skill_name = slugify_name(skill_name)

    if not source.is_dir():
        raise SkillScaffoldError(f"Source directory not found: {source}")

    verify_source_skill(source, skill_name)

    skill_dir = root / SHARED_SKILL_DIR.format(name=skill_name)
    assert_not_replacing_command_skill(source, skill_dir)
    ensure_bridge_symlink(root)
    copy_skill_source(source, skill_dir, overwrite)

    return [skill_dir]


def validate_install(root: Path, skill_name: str, validator_script: Path) -> None:
    path = root / SHARED_SKILL_DIR.format(name=skill_name)
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
        description="Install a bootstrap skill into the single-root portable layout."
    )
    parser.add_argument("--root", required=True, help="Repository root directory.")
    parser.add_argument("--name", required=True, help="Skill name; normalized to hyphen-case.")
    parser.add_argument(
        "--source",
        required=True,
        help="Path to the bootstrap skill directory to copy into .agents/skills/.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        default=True,
        help="Overwrite an existing shared skill install (default: true).",
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
    try:
        written = install_portable_skill(
            root=Path(args.root),
            source=Path(args.source),
            skill_name=args.name,
            overwrite=args.overwrite,
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
        "\nRestart or reload Claude Code so it rediscovers the installed skill "
        "through the .claude/skills bridge."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
