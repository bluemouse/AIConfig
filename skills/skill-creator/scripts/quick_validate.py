#!/usr/bin/env python3
"""
Quick validation for portable skills — bootstrap sources and shared installs.

Bootstrap sources live at skills/<name>/. Installing copies the source
verbatim to the single root .agents/skills/<name>/ (flat layout, no category
subfolders) and bridges Claude Code via the .claude/skills symlink.
Tool-specific guidance lives in `## Tool notes` sections of the SKILL.md body.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

ALLOWED_PROPERTIES = {
    "name",
    "description",
    "license",
    "allowed-tools",
    "metadata",
    "compatibility",
    "disable-model-invocation",
}

SKILL_MODES = ("bootstrap", "shared")

MODE_LABELS = {
    "bootstrap": "Bootstrap skill",
    "shared": "Shared skill",
}


def parse_frontmatter(content: str) -> tuple[dict | None, str | None]:
    if not content.startswith("---"):
        return None, "No YAML frontmatter found"

    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return None, "Invalid frontmatter format"

    try:
        frontmatter = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        return None, f"Invalid YAML in frontmatter: {exc}"

    if not isinstance(frontmatter, dict):
        return None, "Frontmatter must be a YAML dictionary"

    return frontmatter, None


def body_after_frontmatter(content: str) -> str:
    match = re.match(r"^---\n.*?\n---\n?", content, re.DOTALL)
    if not match:
        return content
    return content[match.end() :].strip()


def validate_name(name: str) -> str | None:
    if not isinstance(name, str):
        return f"Name must be a string, got {type(name).__name__}"
    name = name.strip()
    if not name:
        return "Name cannot be empty"
    if not re.match(r"^[a-z0-9-]+$", name):
        return (
            f"Name '{name}' should be kebab-case "
            "(lowercase letters, digits, and hyphens only)"
        )
    if name.startswith("-") or name.endswith("-") or "--" in name:
        return f"Name '{name}' cannot start/end with hyphen or contain consecutive hyphens"
    if len(name) > 64:
        return f"Name is too long ({len(name)} characters). Maximum is 64 characters."
    return None


def validate_description(description: str) -> str | None:
    if not isinstance(description, str):
        return f"Description must be a string, got {type(description).__name__}"
    description = description.strip()
    if not description:
        return "Description cannot be empty"
    if "<" in description or ">" in description:
        return "Description cannot contain angle brackets (< or >)"
    if len(description) > 1024:
        return (
            f"Description is too long ({len(description)} characters). "
            "Maximum is 1024 characters."
        )
    return None


def validate_frontmatter(frontmatter: dict) -> str | None:
    unexpected_keys = set(frontmatter.keys()) - ALLOWED_PROPERTIES
    if unexpected_keys:
        return (
            f"Unexpected key(s) in SKILL.md frontmatter: {', '.join(sorted(unexpected_keys))}. "
            f"Allowed properties are: {', '.join(sorted(ALLOWED_PROPERTIES))}"
        )

    if "name" not in frontmatter:
        return "Missing 'name' in frontmatter"
    if "description" not in frontmatter:
        return "Missing 'description' in frontmatter"

    name_error = validate_name(frontmatter.get("name", ""))
    if name_error:
        return name_error

    description_error = validate_description(frontmatter.get("description", ""))
    if description_error:
        return description_error

    compatibility = frontmatter.get("compatibility", "")
    if compatibility:
        if not isinstance(compatibility, str):
            return f"Compatibility must be a string, got {type(compatibility).__name__}"
        if len(compatibility) > 500:
            return (
                f"Compatibility is too long ({len(compatibility)} characters). "
                "Maximum is 500 characters."
            )

    return None


def detect_mode(skill_path: Path) -> str:
    """Detect whether a skill directory is a bootstrap source or a shared install.

    Installed skills live under .agents/skills/<name>/. Bootstrap sources live
    at skills/<name>/ in the bootstrap tree. The .claude/skills bridge symlink
    resolves to .agents/skills/, so bridged paths classify as shared.
    """
    parts = Path(skill_path).resolve().parts
    if ".agents" in parts:
        return "shared"
    return "bootstrap"


def validate_flat_root(skill_path: Path) -> str | None:
    """Reject category subfolders: a skill dir must be a direct child of a skills root.

    Validated by structure (the parent directory is named 'skills'), not by
    absolute location, so bootstrap (skills/<name>/) and installed
    (.agents/skills/<name>/) layouts both pass.
    """
    parent_name = skill_path.parent.name
    if parent_name != "skills":
        return (
            f"Skill directory '{skill_path.name}' must be a direct child of a "
            f"skills root; found it under '{parent_name}/'. The single-root "
            "layout is flat: .agents/skills/<name>/ with no category subfolders."
        )
    return None


def validate_skill_dir(skill_path: Path, mode: str) -> tuple[bool, str]:
    """Validate a skill directory containing SKILL.md, in any kept mode."""
    root_error = validate_flat_root(skill_path)
    if root_error:
        return False, root_error

    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return False, "SKILL.md not found"

    content = skill_md.read_text(encoding="utf-8")
    frontmatter, error = parse_frontmatter(content)
    if error:
        return False, error

    frontmatter_error = validate_frontmatter(frontmatter)
    if frontmatter_error:
        return False, frontmatter_error

    name = frontmatter["name"].strip()
    if skill_path.name != name:
        return False, f"Directory name '{skill_path.name}' must match frontmatter name '{name}'"

    return True, f"{MODE_LABELS[mode]} is valid!"


def validate_bootstrap_skill(skill_path: Path) -> tuple[bool, str]:
    """Validate a bootstrap source skill directory (skills/<name>/)."""
    return validate_skill_dir(skill_path, "bootstrap")


def validate_shared_skill(skill_path: Path) -> tuple[bool, str]:
    """Validate a shared/installed skill directory (.agents/skills/<name>/)."""
    return validate_skill_dir(skill_path, "shared")


def validate_skill(skill_path: Path, mode: str | None = None) -> tuple[bool, str]:
    skill_path = Path(skill_path)
    if not skill_path.is_dir():
        return False, f"Skill path is not a directory: {skill_path}"

    resolved_mode = mode or detect_mode(skill_path)
    if resolved_mode == "bootstrap":
        return validate_bootstrap_skill(skill_path)
    return validate_shared_skill(skill_path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate a bootstrap or shared/installed skill directory."
    )
    parser.add_argument("skill_path", help="Path to the skill directory")
    parser.add_argument(
        "--mode",
        choices=SKILL_MODES,
        help="Validation mode (auto-detected when omitted)",
    )
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])

    valid, message = validate_skill(args.skill_path, args.mode)
    print(message)
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
