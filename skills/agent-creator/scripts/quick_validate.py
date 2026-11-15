#!/usr/bin/env python3
"""
Quick validation for portable agents — bootstrap AGENT.md and dual-target installs.

Agents install as two real copies: .claude/agents/<name>.md (verbatim AGENT.md)
and .github/agents/<name>.agent.md (Copilot transform). There is no shared
wrapper layer; tool-specific guidance lives in `## Tool notes` sections of
AGENT.md.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

CLAUDE_AGENT_PATH = ".claude/agents/{name}.md"
GITHUB_AGENT_PATH = ".github/agents/{name}.agent.md"

AGENT_MODES = ("bootstrap", "claude", "github")

MODE_LABELS = {
    "bootstrap": "Bootstrap agent",
    "claude": "Claude Code agent",
    "github": "GitHub Copilot agent",
}

GITHUB_ALLOWED_KEYS = {"name", "description"}

TOOL_NOTES_HEADING = "## Tool notes"

TOOL_NEUTRALITY_PATTERNS = (
    re.compile(r"\bCursor window\b", re.IGNORECASE),
    re.compile(r"\bTask tool\b", re.IGNORECASE),
    re.compile(r"\bGitHub Copilot\b", re.IGNORECASE),
    re.compile(r"\bClaude Code\b", re.IGNORECASE),
    re.compile(r"\bclaude -p\b", re.IGNORECASE),
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


def detect_mode(agent_path: Path) -> str:
    agent_path = Path(agent_path)
    if agent_path.name == "AGENT.md":
        return "bootstrap"
    parts = {part.lower() for part in agent_path.resolve().parts}
    if ".github" in parts:
        return "github"
    return "claude"


def expected_filename(name: str, mode: str, agent_path: Path) -> str | None:
    if mode == "bootstrap":
        if agent_path.name == "AGENT.md":
            return None
        return "AGENT.md"
    if mode == "github":
        expected = f"{name}.agent.md"
    else:
        expected = f"{name}.md"
    if agent_path.name != expected:
        return expected
    return None


def split_tool_notes(body: str) -> tuple[str, str]:
    """Split a body into (tool-neutral body, `## Tool notes` section)."""
    match = re.search(r"^## Tool notes\s*$", body, re.MULTILINE)
    if not match:
        return body, ""
    return body[: match.start()], body[match.start() :]


def validate_agent_file(agent_path: Path, *, mode: str) -> tuple[bool, str]:
    if not agent_path.is_file():
        return False, f"Agent path is not a file: {agent_path}"

    content = agent_path.read_text(encoding="utf-8")
    frontmatter, error = parse_frontmatter(content)
    if error:
        return False, error

    if "name" not in frontmatter:
        return False, "Missing 'name' in frontmatter"
    if "description" not in frontmatter:
        return False, "Missing 'description' in frontmatter"

    name = frontmatter["name"]
    if isinstance(name, str):
        name = name.strip()
    name_error = validate_name(name)
    if name_error:
        return False, name_error

    description_error = validate_description(frontmatter.get("description", ""), strict=True)
    if description_error:
        return False, description_error

    if mode == "github":
        unexpected_keys = set(frontmatter.keys()) - GITHUB_ALLOWED_KEYS
        if unexpected_keys:
            return (
                False,
                "Unexpected key(s) in GitHub Copilot agent frontmatter: "
                f"{', '.join(sorted(unexpected_keys))}. Copilot agents support "
                f"{', '.join(sorted(GITHUB_ALLOWED_KEYS))}; move tool-specific "
                "settings into a '## Tool notes' section.",
            )

    filename_error = expected_filename(name, mode, agent_path)
    if filename_error:
        return False, f"Filename '{agent_path.name}' must be '{filename_error}'"

    body = body_after_frontmatter(content)
    if not body:
        return False, "Agent body cannot be empty"

    neutral_body, _tool_notes = split_tool_notes(body)
    for pattern in TOOL_NEUTRALITY_PATTERNS:
        if pattern.search(neutral_body):
            return (
                False,
                f"Agent body appears tool-specific ({pattern.pattern}). "
                f"Move tool-specific details into a '{TOOL_NOTES_HEADING}' section.",
            )

    return True, f"{MODE_LABELS[mode]} is valid!"


def validate_agent(agent_path: Path, mode: str | None = None) -> tuple[bool, str]:
    agent_path = Path(agent_path)
    resolved_mode = mode or detect_mode(agent_path)
    return validate_agent_file(agent_path, mode=resolved_mode)


def validate_bootstrap_agent(source: Path) -> tuple[bool, list[str]]:
    source = source.resolve()
    messages: list[str] = []
    all_valid = True

    agent_md = source / "AGENT.md"
    valid, message = validate_agent_file(agent_md, mode="bootstrap")
    messages.append(f"{agent_md}: {message}")
    all_valid = all_valid and valid

    agent_name = ""
    if agent_md.is_file():
        frontmatter, _ = parse_frontmatter(agent_md.read_text(encoding="utf-8"))
        if frontmatter and isinstance(frontmatter.get("name"), str):
            agent_name = frontmatter["name"].strip()

    if all_valid and agent_name:
        messages.append(f"Bootstrap agent '{agent_name}' is valid.")
    return all_valid, messages


def check_target_sync(
    claude_path: Path,
    github_path: Path,
    agent_name: str,
) -> list[str]:
    messages: list[str] = []

    descriptions: dict[str, str] = {}
    for label, path in (("Claude Code", claude_path), ("GitHub Copilot", github_path)):
        frontmatter, _ = parse_frontmatter(path.read_text(encoding="utf-8"))
        if not frontmatter:
            continue
        name = frontmatter.get("name", "")
        if isinstance(name, str) and name.strip() != agent_name:
            messages.append(
                f"{path}: name '{name.strip()}' does not match agent name '{agent_name}'"
            )
        description = frontmatter.get("description", "")
        if isinstance(description, str):
            descriptions[label] = normalize_description(description)

    if "Claude Code" in descriptions and "GitHub Copilot" in descriptions:
        if descriptions["Claude Code"] != descriptions["GitHub Copilot"]:
            messages.append(
                f"{github_path}: description does not match Claude Code agent description"
            )

    return messages


def validate_portable_agent(root: Path, name: str) -> tuple[bool, list[str]]:
    root = root.resolve()
    agent_name = name.strip()
    messages: list[str] = []
    all_valid = True

    claude_path = root / CLAUDE_AGENT_PATH.format(name=agent_name)
    github_path = root / GITHUB_AGENT_PATH.format(name=agent_name)

    for path, mode in ((claude_path, "claude"), (github_path, "github")):
        if not path.is_file():
            all_valid = False
            messages.append(f"{path}: Installed agent file not found")
            continue
        valid, message = validate_agent_file(path, mode=mode)
        messages.append(f"{path}: {message}")
        all_valid = all_valid and valid

    if all_valid:
        for sync_error in check_target_sync(claude_path, github_path, agent_name):
            messages.append(sync_error)
            all_valid = False

    if all_valid:
        messages.append(
            f"Portable agent '{agent_name}' is valid across 2 installed file(s)."
        )
    return all_valid, messages


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate a bootstrap or installed agent file, or a full agent set."
    )
    parser.add_argument(
        "agent_path",
        nargs="?",
        help="Path to a bootstrap AGENT.md or installed agent markdown file",
    )
    parser.add_argument(
        "--root",
        help="Repository root when validating a full installed agent set",
    )
    parser.add_argument(
        "--name",
        help="Agent name when validating a full installed agent set (used with --root)",
    )
    parser.add_argument(
        "--mode",
        choices=AGENT_MODES,
        help="Validation mode (auto-detected when omitted)",
    )
    parser.add_argument(
        "--bootstrap-source",
        help="Path to a bootstrap agent directory (agents/<name>/) to validate AGENT.md",
    )
    args = parser.parse_args(argv)

    if args.bootstrap_source:
        valid, messages = validate_bootstrap_agent(Path(args.bootstrap_source))
        for message in messages:
            print(message)
        return 0 if valid else 1

    if args.root and args.name:
        valid, messages = validate_portable_agent(Path(args.root), args.name)
        for message in messages:
            print(message)
        return 0 if valid else 1

    if not args.agent_path:
        parser.error("Provide agent_path or both --root and --name")

    if args.root or args.name:
        parser.error("--root and --name must be used together")

    valid, message = validate_agent(args.agent_path, args.mode)
    print(message)
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
