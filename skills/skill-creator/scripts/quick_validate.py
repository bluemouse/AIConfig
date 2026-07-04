#!/usr/bin/env python3
"""
Quick validation script for skills - shared packages and tool wrappers.
"""

import argparse
import re
import sys

import yaml
from pathlib import Path

ALLOWED_PROPERTIES = {
    "name",
    "description",
    "license",
    "allowed-tools",
    "metadata",
    "compatibility",
    "disable-model-invocation",
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


def validate_frontmatter(frontmatter: dict, *, strict: bool) -> str | None:
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
    if description_error and strict:
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
    parts = skill_path.resolve().parts
    if ".shared" in parts and "skills" in parts:
        return "shared"
    tool_markers = {".cursor", ".claude", ".github"}
    if any(marker in parts for marker in tool_markers) and "skills" in parts:
        return "wrapper"
    return "shared"


def expected_shared_reference(skill_name: str) -> str:
    return f"../../../.shared/skills/{skill_name}/SKILL.md"


def validate_shared_skill(skill_path: Path) -> tuple[bool, str]:
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return False, "SKILL.md not found"

    content = skill_md.read_text()
    frontmatter, error = parse_frontmatter(content)
    if error:
        return False, error

    frontmatter_error = validate_frontmatter(frontmatter, strict=True)
    if frontmatter_error:
        return False, frontmatter_error

    name = frontmatter["name"].strip()
    if skill_path.name != name:
        return False, f"Directory name '{skill_path.name}' must match frontmatter name '{name}'"

    return True, "Shared skill is valid!"


def validate_wrapper_skill(skill_path: Path) -> tuple[bool, str]:
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return False, "SKILL.md not found"

    extra_entries = [p.name for p in skill_path.iterdir() if p.name != "SKILL.md"]
    if extra_entries:
        return (
            False,
            "Wrapper skill directories should contain only SKILL.md; "
            f"found: {', '.join(sorted(extra_entries))}",
        )

    content = skill_md.read_text()
    frontmatter, error = parse_frontmatter(content)
    if error:
        return False, error

    frontmatter_error = validate_frontmatter(frontmatter, strict=False)
    if frontmatter_error:
        return False, frontmatter_error

    name = frontmatter["name"].strip()
    if skill_path.name != name:
        return False, f"Directory name '{skill_path.name}' must match frontmatter name '{name}'"

    shared_ref = expected_shared_reference(name)
    if shared_ref not in content:
        return (
            False,
            f"Wrapper body must reference the shared skill path: {shared_ref}",
        )

    if "wrapper" not in content.lower():
        return False, "Wrapper body should identify itself as a tool-specific wrapper"

    return True, "Wrapper skill is valid!"


def validate_skill(skill_path: Path, mode: str | None = None) -> tuple[bool, str]:
    skill_path = Path(skill_path)
    if not skill_path.is_dir():
        return False, f"Skill path is not a directory: {skill_path}"

    resolved_mode = mode or detect_mode(skill_path)
    if resolved_mode == "wrapper":
        return validate_wrapper_skill(skill_path)
    return validate_shared_skill(skill_path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a shared or wrapper skill directory.")
    parser.add_argument("skill_path", help="Path to the skill directory")
    parser.add_argument(
        "--mode",
        choices=("shared", "wrapper"),
        help="Validation mode (auto-detected when omitted)",
    )
    args = parser.parse_args()

    valid, message = validate_skill(args.skill_path, args.mode)
    print(message)
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
