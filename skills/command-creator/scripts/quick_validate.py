#!/usr/bin/env python3
"""
Quick validation for portable commands — shared files and tool install outputs.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

SHARED_ALLOWED_KEYS = {"name", "description"}

CLAUDE_ALLOWED_KEYS = {
    "name",
    "description",
    "argument-hint",
    "allowed-tools",
    "model",
    "disable-model-invocation",
    "user-invocable",
    "context",
    "agent",
}

GITHUB_ALLOWED_KEYS = {
    "name",
    "description",
    "argument-hint",
    "agent",
    "model",
    "tools",
}

TOOL_PATHS = {
    "cursor": ".cursor/commands/{name}.md",
    "claude": ".claude/commands/{name}.md",
    "github": ".github/prompts/{name}.prompt.md",
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


def validate_description(description: str, *, strict: bool) -> str | None:
    if not isinstance(description, str):
        return f"Description must be a string, got {type(description).__name__}"
    description = description.strip()
    if not description:
        return "Description cannot be empty"
    if strict and ("<" in description or ">" in description):
        return "Description cannot contain angle brackets (< or >)"
    if len(description) > 1024:
        return (
            f"Description is too long ({len(description)} characters). "
            "Maximum is 1024 characters."
        )
    return None


def normalize_description(description: str) -> str:
    return " ".join(description.strip().split())


def detect_mode(command_path: Path) -> str:
    parts = command_path.resolve().parts
    if command_path.name == "COMMAND.md":
        parent = command_path.parent
        if parent.parent.name == "wrappers" or parent.name == "wrappers":
            tool = parent.name if parent.parent.name == "wrappers" else ""
            if tool == "cursor":
                return "bootstrap_cursor_wrapper"
            return "bootstrap_wrapper"
        if parent.parent.name == "commands" or parent.name == "commands":
            return "bootstrap_shared"
    if ".shared" in parts and "commands" in parts:
        return "shared"
    if ".cursor" in parts and "commands" in parts:
        return "cursor"
    if ".claude" in parts and "commands" in parts:
        return "claude"
    if ".github" in parts and "prompts" in parts:
        return "github"
    return "shared"


def validate_shared_command(command_path: Path, *, mode: str = "shared") -> tuple[bool, str]:
    if not command_path.is_file():
        return False, f"Shared command path is not a file: {command_path}"

    content = command_path.read_text(encoding="utf-8")
    frontmatter, error = parse_frontmatter(content)
    if error:
        return False, error

    unexpected_keys = set(frontmatter.keys()) - SHARED_ALLOWED_KEYS
    if unexpected_keys:
        return (
            False,
            "Unexpected key(s) in shared command frontmatter: "
            f"{', '.join(sorted(unexpected_keys))}. "
            f"Allowed properties are: {', '.join(sorted(SHARED_ALLOWED_KEYS))}",
        )

    if "name" not in frontmatter:
        return False, "Missing 'name' in frontmatter"
    if "description" not in frontmatter:
        return False, "Missing 'description' in frontmatter"

    name = frontmatter["name"].strip()
    name_error = validate_name(name)
    if name_error:
        return False, name_error

    description_error = validate_description(frontmatter.get("description", ""), strict=True)
    if description_error:
        return False, description_error

    if mode == "bootstrap_shared" and command_path.name != "COMMAND.md":
        return False, "Bootstrap shared command file must be named COMMAND.md"

    if mode == "shared":
        expected = f"{name}.md"
        if command_path.name != expected:
            return False, f"Filename '{command_path.name}' must be '{expected}'"

    body = body_after_frontmatter(content)
    if not body:
        return False, "Shared command body cannot be empty"

    if mode in {"bootstrap_shared", "shared"}:
        for pattern in TOOL_NEUTRALITY_PATTERNS:
            if pattern.search(body):
                return (
                    False,
                    f"Shared command body appears tool-specific ({pattern.pattern}). "
                    "Move tool-native details into wrappers.",
                )

    label = "Bootstrap shared command" if mode == "bootstrap_shared" else "Shared command"
    return True, f"{label} is valid!"


def validate_cursor_command(command_path: Path) -> tuple[bool, str]:
    if not command_path.is_file():
        return False, f"Cursor command path is not a file: {command_path}"

    content = command_path.read_text(encoding="utf-8")
    if content.strip().startswith("---"):
        return False, "Cursor command must not contain YAML frontmatter"

    if not content.strip():
        return False, "Cursor command body cannot be empty"

    if not command_path.name.endswith(".md") or command_path.name.endswith(".prompt.md"):
        return False, "Cursor command filename must be '<name>.md'"

    return True, "Cursor command is valid!"


def validate_claude_command(command_path: Path, *, mode: str = "claude") -> tuple[bool, str]:
    if not command_path.is_file():
        return False, f"Claude command path is not a file: {command_path}"

    content = command_path.read_text(encoding="utf-8")
    frontmatter, error = parse_frontmatter(content)
    if error:
        return False, error

    unexpected_keys = set(frontmatter.keys()) - CLAUDE_ALLOWED_KEYS
    if unexpected_keys:
        return (
            False,
            "Unexpected key(s) in Claude command frontmatter: "
            f"{', '.join(sorted(unexpected_keys))}",
        )

    if "name" not in frontmatter:
        return False, "Missing 'name' in frontmatter"
    if "description" not in frontmatter:
        return False, "Missing 'description' in frontmatter"

    name = frontmatter["name"].strip()
    name_error = validate_name(name)
    if name_error:
        return False, name_error

    description_error = validate_description(frontmatter.get("description", ""), strict=False)
    if description_error:
        return False, description_error

    if mode == "bootstrap_wrapper" and command_path.name != "COMMAND.md":
        return False, "Bootstrap Claude wrapper must be named COMMAND.md"

    if mode == "claude":
        expected = f"{name}.md"
        if command_path.name != expected:
            return False, f"Filename '{command_path.name}' must be '{expected}'"

    body = body_after_frontmatter(content)
    if not body:
        return False, "Claude command body cannot be empty"

    label = "Bootstrap Claude wrapper" if mode == "bootstrap_wrapper" else "Claude command"
    return True, f"{label} is valid!"


def validate_github_prompt(command_path: Path, *, mode: str = "github") -> tuple[bool, str]:
    if not command_path.is_file():
        return False, f"GitHub prompt path is not a file: {command_path}"

    if not command_path.name.endswith(".prompt.md"):
        return False, "GitHub prompt filename must end with '.prompt.md'"

    content = command_path.read_text(encoding="utf-8")
    frontmatter, error = parse_frontmatter(content)
    if error:
        return False, error

    unexpected_keys = set(frontmatter.keys()) - GITHUB_ALLOWED_KEYS
    if unexpected_keys:
        return (
            False,
            "Unexpected key(s) in GitHub prompt frontmatter: "
            f"{', '.join(sorted(unexpected_keys))}",
        )

    if "description" not in frontmatter:
        return False, "Missing 'description' in frontmatter"

    name = frontmatter.get("name", command_path.stem.replace(".prompt", ""))
    if isinstance(name, str):
        name_error = validate_name(name.strip())
        if name_error:
            return False, name_error

    description_error = validate_description(frontmatter.get("description", ""), strict=False)
    if description_error:
        return False, description_error

    if mode == "bootstrap_wrapper" and command_path.name != "COMMAND.md":
        return False, "Bootstrap GitHub wrapper must be named COMMAND.md"

    if mode == "github" and "name" in frontmatter:
        expected = f"{frontmatter['name'].strip()}.prompt.md"
        if command_path.name != expected:
            return False, f"Filename '{command_path.name}' must be '{expected}'"

    body = body_after_frontmatter(content)
    if not body:
        return False, "GitHub prompt body cannot be empty"

    label = "Bootstrap GitHub wrapper" if mode == "bootstrap_wrapper" else "GitHub prompt"
    return True, f"{label} is valid!"


def validate_bootstrap_cursor_wrapper(command_path: Path) -> tuple[bool, str]:
    if not command_path.is_file():
        return False, f"Bootstrap Cursor wrapper path is not a file: {command_path}"

    content = command_path.read_text(encoding="utf-8")
    if content.strip().startswith("---"):
        return False, "Cursor wrapper must not contain YAML frontmatter"
    if command_path.name != "COMMAND.md":
        return False, "Bootstrap Cursor wrapper must be named COMMAND.md"
    return True, "Bootstrap Cursor wrapper is valid!"


def validate_command(command_path: Path, mode: str | None = None) -> tuple[bool, str]:
    command_path = Path(command_path)
    resolved_mode = mode or detect_mode(command_path)
    if resolved_mode == "cursor":
        return validate_cursor_command(command_path)
    if resolved_mode == "claude":
        return validate_claude_command(command_path)
    if resolved_mode == "github":
        return validate_github_prompt(command_path)
    if resolved_mode == "bootstrap_wrapper":
        return validate_claude_command(command_path, mode="bootstrap_wrapper")
    if resolved_mode == "bootstrap_cursor_wrapper":
        return validate_bootstrap_cursor_wrapper(command_path)
    return validate_shared_command(command_path, mode=resolved_mode)


def validate_bootstrap_command(source: Path) -> tuple[bool, list[str]]:
    source = source.resolve()
    messages: list[str] = []
    all_valid = True

    command_md = source / "COMMAND.md"
    valid, message = validate_shared_command(command_md, mode="bootstrap_shared")
    messages.append(f"{command_md}: {message}")
    all_valid = all_valid and valid

    wrappers_dir = source / "wrappers"
    if wrappers_dir.is_dir():
        for wrapper_path in sorted(wrappers_dir.glob("*/COMMAND.md")):
            tool = wrapper_path.parent.name
            if tool == "cursor":
                valid, message = validate_bootstrap_cursor_wrapper(wrapper_path)
            elif tool == "claude":
                valid, message = validate_claude_command(wrapper_path, mode="bootstrap_wrapper")
            elif tool == "github":
                valid, message = validate_github_prompt(wrapper_path, mode="bootstrap_wrapper")
            else:
                valid, message = False, f"Unknown wrapper tool '{tool}'"
            messages.append(f"{wrapper_path}: {message}")
            all_valid = all_valid and valid

    if all_valid and command_md.is_file():
        frontmatter, _ = parse_frontmatter(command_md.read_text(encoding="utf-8"))
        if frontmatter and isinstance(frontmatter.get("name"), str):
            messages.append(f"Bootstrap command '{frontmatter['name'].strip()}' is valid.")
    return all_valid, messages


def validate_portable_command(root: Path, name: str) -> tuple[bool, list[str]]:
    root = root.resolve()
    command_name = name.strip()
    messages: list[str] = []
    all_valid = True

    shared_path = root / ".shared" / "commands" / f"{command_name}.md"
    valid, message = validate_shared_command(shared_path)
    messages.append(f"{shared_path}: {message}")
    all_valid = all_valid and valid

    cursor_path = root / TOOL_PATHS["cursor"].format(name=command_name)
    valid, message = validate_cursor_command(cursor_path)
    messages.append(f"{cursor_path}: {message}")
    all_valid = all_valid and valid

    claude_path = root / TOOL_PATHS["claude"].format(name=command_name)
    valid, message = validate_claude_command(claude_path)
    messages.append(f"{claude_path}: {message}")
    all_valid = all_valid and valid

    github_path = root / TOOL_PATHS["github"].format(name=command_name)
    valid, message = validate_github_prompt(github_path)
    messages.append(f"{github_path}: {message}")
    all_valid = all_valid and valid

    if all_valid:
        messages.append(
            f"Portable command '{command_name}' is valid across 4 installed file(s)."
        )
    return all_valid, messages


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate a shared or tool command file, or a full portable command set."
    )
    parser.add_argument(
        "command_path",
        nargs="?",
        help="Path to a command markdown file",
    )
    parser.add_argument(
        "--root",
        help="Repository root when validating a full portable command set",
    )
    parser.add_argument(
        "--name",
        help="Command name when validating a full portable command set (used with --root)",
    )
    parser.add_argument(
        "--mode",
        choices=(
            "shared",
            "bootstrap_shared",
            "cursor",
            "claude",
            "github",
            "bootstrap_wrapper",
            "bootstrap_cursor_wrapper",
        ),
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
    if command_path.is_dir() and (command_path / "COMMAND.md").is_file():
        valid, messages = validate_bootstrap_command(command_path)
        for message in messages:
            print(message)
        return 0 if valid else 1

    valid, message = validate_command(args.command_path, args.mode)
    print(message)
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
