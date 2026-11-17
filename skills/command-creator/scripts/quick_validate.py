#!/usr/bin/env python3
"""
Quick validation for portable commands — bootstrap sources and command-skills.

A bootstrap command lives at commands/<name>/COMMAND.md. Installing it writes
a command-skill: .agents/skills/<install-dir>/SKILL.md (install dir =
COMMAND_SKILL_DIR_PREFIX + <name>) with `disable-model-invocation: true`
and an invocation-gated description, so every coding agent can invoke it
as /<name> and the model never self-invokes it. The dir prefix keeps
command-skills visually distinct from plain skills in the shared
.agents/skills/ namespace without lengthening the slash name.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

BOOTSTRAP_COMMAND_FILENAME = "COMMAND.md"
COMMAND_SKILL_FILENAME = "SKILL.md"
COMMAND_SKILL_DIR_PARTS = (".agents", "skills")

# Installed command-skills live at .agents/skills/<prefix><name>/ while the
# slash command stays /<name>: the frontmatter name is the invocation
# identity, the directory is just storage. Twin sites (cr-010): tools/
# installer.py:COMMAND_SKILL_DIR_PREFIX mirrors this constant — change both.
COMMAND_SKILL_DIR_PREFIX = "cmd-"

MAX_DESCRIPTION_LENGTH = 120
INVOCATION_GATE_PATTERN = re.compile(r"explicitly invokes", re.IGNORECASE)

BOOTSTRAP_ALLOWED_KEYS = {"name", "description", "allowed-tools"}
COMMAND_SKILL_ALLOWED_KEYS = {
    "name",
    "description",
    "disable-model-invocation",
    "allowed-tools",
}

TOOL_NEUTRALITY_PATTERNS = (
    re.compile(r"\bCursor window\b", re.IGNORECASE),
    re.compile(r"\bGitHub Copilot\b", re.IGNORECASE),
    re.compile(r"\bClaude Code\b", re.IGNORECASE),
    re.compile(r"\bVS Code\b", re.IGNORECASE),
)


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


def command_skill_dir_name(name: str) -> str:
    """Return the .agents/skills/ directory name for a command's install."""
    return f"{COMMAND_SKILL_DIR_PREFIX}{name}"


def validate_description(description: str) -> str | None:
    """Command descriptions must be <=120 chars and invocation-gated."""
    if not isinstance(description, str):
        return f"Description must be a string, got {type(description).__name__}"
    description = description.strip()
    if not description:
        return "Description cannot be empty"
    if len(description) > MAX_DESCRIPTION_LENGTH:
        return (
            f"Description is too long ({len(description)} characters). "
            f"Maximum is {MAX_DESCRIPTION_LENGTH} characters."
        )
    if not INVOCATION_GATE_PATTERN.search(description):
        return (
            "Description must be invocation-gated: state that the user explicitly "
            "invokes the command (e.g. \"... when the user explicitly invokes /<name>.\")"
        )
    return None


def detect_mode(command_path: Path) -> str:
    """Detect whether a file is a bootstrap source or an installed command-skill."""
    if command_path.resolve().name == BOOTSTRAP_COMMAND_FILENAME:
        return "bootstrap_shared"
    return "command_skill"


def validate_bootstrap_shared(command_path: Path) -> tuple[bool, str]:
    """Validate a bootstrap source COMMAND.md (commands/<name>/COMMAND.md)."""
    if not command_path.is_file():
        return False, f"Bootstrap command path is not a file: {command_path}"

    content = command_path.read_text(encoding="utf-8")
    frontmatter, error = parse_frontmatter(content)
    if error:
        return False, error

    unexpected_keys = set(frontmatter.keys()) - BOOTSTRAP_ALLOWED_KEYS
    if unexpected_keys:
        return (
            False,
            "Unexpected key(s) in bootstrap command frontmatter: "
            f"{', '.join(sorted(unexpected_keys))}. "
            f"Allowed properties are: {', '.join(sorted(BOOTSTRAP_ALLOWED_KEYS))}",
        )

    if "name" not in frontmatter:
        return False, "Missing 'name' in frontmatter"
    if "description" not in frontmatter:
        return False, "Missing 'description' in frontmatter"

    name = str(frontmatter["name"]).strip()
    name_error = validate_name(name)
    if name_error:
        return False, name_error

    if command_path.name != BOOTSTRAP_COMMAND_FILENAME:
        return False, f"Bootstrap command file must be named '{BOOTSTRAP_COMMAND_FILENAME}'"

    parent_name = command_path.parent.name
    if parent_name != name:
        return (
            False,
            f"Bootstrap source directory '{parent_name}' must match the command name '{name}'",
        )

    description_error = validate_description(frontmatter.get("description", ""))
    if description_error:
        return False, description_error

    body = body_after_frontmatter(content)
    if not body:
        return False, "Bootstrap command body cannot be empty"

    for pattern in TOOL_NEUTRALITY_PATTERNS:
        if pattern.search(body):
            return (
                False,
                f"Bootstrap command body appears tool-specific ({pattern.pattern}). "
                "Keep the command body agent-neutral.",
            )

    return True, "Bootstrap command is valid!"


def validate_command_skill(command_path: Path) -> tuple[bool, str]:
    """Validate an installed command-skill (.agents/skills/<name>/SKILL.md)."""
    if not command_path.is_file():
        return False, f"Command skill path is not a file: {command_path}"

    content = command_path.read_text(encoding="utf-8")
    frontmatter, error = parse_frontmatter(content)
    if error:
        return False, error

    unexpected_keys = set(frontmatter.keys()) - COMMAND_SKILL_ALLOWED_KEYS
    if unexpected_keys:
        return (
            False,
            "Unexpected key(s) in command skill frontmatter: "
            f"{', '.join(sorted(unexpected_keys))}. "
            f"Allowed properties are: {', '.join(sorted(COMMAND_SKILL_ALLOWED_KEYS))}",
        )

    if "name" not in frontmatter:
        return False, "Missing 'name' in frontmatter"
    if "description" not in frontmatter:
        return False, "Missing 'description' in frontmatter"

    name = str(frontmatter["name"]).strip()
    name_error = validate_name(name)
    if name_error:
        return False, name_error

    description_error = validate_description(frontmatter.get("description", ""))
    if description_error:
        return False, description_error

    flag = frontmatter.get("disable-model-invocation")
    if flag is not True:
        return (
            False,
            "Command skill 'disable-model-invocation' must be true; commands are "
            f"slash-invoked only (got {flag!r})",
        )

    if command_path.name != COMMAND_SKILL_FILENAME:
        return False, f"Filename '{command_path.name}' must be '{COMMAND_SKILL_FILENAME}'"

    parent_name = command_path.parent.name
    if parent_name != command_skill_dir_name(name):
        return (
            False,
            f"Command skill directory '{parent_name}' must be "
            f"'{command_skill_dir_name(name)}' (command dir prefix + name '{name}')",
        )

    body = body_after_frontmatter(content)
    if not body:
        return False, "Command skill body cannot be empty"

    for pattern in TOOL_NEUTRALITY_PATTERNS:
        if pattern.search(body):
            return (
                False,
                f"Command skill body appears tool-specific ({pattern.pattern}). "
                "Keep the command body agent-neutral.",
            )

    return True, "Command skill is valid!"


def validate_command(command_path: Path, mode: str | None = None) -> tuple[bool, str]:
    command_path = Path(command_path)
    resolved_mode = mode or detect_mode(command_path)
    if resolved_mode == "bootstrap_shared":
        return validate_bootstrap_shared(command_path)
    return validate_command_skill(command_path)


def validate_bootstrap_command(source: Path) -> tuple[bool, list[str]]:
    source = source.resolve()
    messages: list[str] = []
    all_valid = True

    command_md = source / BOOTSTRAP_COMMAND_FILENAME
    valid, message = validate_bootstrap_shared(command_md)
    messages.append(f"{command_md}: {message}")
    all_valid = all_valid and valid

    if all_valid and command_md.is_file():
        frontmatter, _ = parse_frontmatter(command_md.read_text(encoding="utf-8"))
        if frontmatter and isinstance(frontmatter.get("name"), str):
            messages.append(f"Bootstrap command '{frontmatter['name'].strip()}' is valid.")
    return all_valid, messages


def validate_portable_command(root: Path, name: str) -> tuple[bool, list[str]]:
    root = root.resolve()
    command_name = name.strip()
    skill_path = (
        root.joinpath(*COMMAND_SKILL_DIR_PARTS)
        / command_skill_dir_name(command_name)
        / COMMAND_SKILL_FILENAME
    )
    valid, message = validate_command_skill(skill_path)
    messages = [f"{skill_path}: {message}"]
    if valid:
        messages.append(
            f"Portable command '{command_name}' is valid as a command skill "
            f"at {skill_path}."
        )
    return valid, messages


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate a command-skill, a bootstrap command source, or an installed command."
    )
    parser.add_argument(
        "command_path",
        nargs="?",
        help="Path to a command markdown file",
    )
    parser.add_argument(
        "--root",
        help="Repository root when validating an installed command",
    )
    parser.add_argument(
        "--name",
        help="Command name when validating an installed command (used with --root)",
    )
    parser.add_argument(
        "--mode",
        choices=("command_skill", "bootstrap_shared"),
        help="Validation mode (auto-detected when omitted)",
    )
    parser.add_argument(
        "--bootstrap-source",
        help="Path to a bootstrap command directory (commands/<name>/)",
    )
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])

    if args.bootstrap_source:
        valid, messages = validate_bootstrap_command(Path(args.bootstrap_source))
        for message in messages:
            print(message)
        return 0 if valid else 1

    if args.root and args.name:
        valid, messages = validate_portable_command(Path(args.root), args.name)
        for message in messages:
            print(message)
        return 0 if valid else 1

    if not args.command_path:
        parser.error("Provide command_path or both --root and --name")

    if args.root or args.name:
        parser.error("--root and --name must be used together")

    command_path = Path(args.command_path)
    if command_path.is_dir() and (command_path / BOOTSTRAP_COMMAND_FILENAME).is_file():
        valid, messages = validate_bootstrap_command(command_path)
        for message in messages:
            print(message)
        return 0 if valid else 1

    valid, message = validate_command(args.command_path, args.mode)
    print(message)
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
