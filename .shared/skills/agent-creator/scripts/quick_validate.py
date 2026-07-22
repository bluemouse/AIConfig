#!/usr/bin/env python3
"""
Quick validation for portable agents — shared files and tool wrappers.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

SHARED_ALLOWED_KEYS = {"name", "description"}

WRAPPER_PATHS = {
    "claude": ".claude/agents/{name}.md",
    "cursor": ".cursor/agents/{name}.md",
    "github": ".github/agents/{name}.agent.md",
}

RELATIVE_SHARED_PATH = "../../.shared/agents/{name}.md"

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
    parts = agent_path.resolve().parts
    if agent_path.name == "AGENT.md":
        parent = agent_path.parent
        if parent.parent.name == "wrappers" or parent.name == "wrappers":
            return "bootstrap_wrapper"
        if parent.parent.name == "agents":
            return "bootstrap_shared"
    if ".shared" in parts and "agents" in parts:
        return "shared"
    tool_markers = {".cursor", ".claude", ".github"}
    if any(marker in parts for marker in tool_markers) and "agents" in parts:
        return "wrapper"
    return "shared"


def expected_filename(name: str, mode: str, agent_path: Path) -> str | None:
    if mode in {"bootstrap_shared", "bootstrap_wrapper"}:
        if agent_path.name == "AGENT.md":
            return None
        return "AGENT.md"
    if mode == "shared":
        expected = f"{name}.md"
        if agent_path.name != expected:
            return expected
        return None
    if agent_path.parts[-2:] == ("agents", f"{name}.md"):
        return None
    if agent_path.parts[-2:] == ("agents", f"{name}.agent.md"):
        return None
    if ".github" in agent_path.parts:
        return f"{name}.agent.md"
    return f"{name}.md"


def validate_shared_agent(agent_path: Path, *, mode: str = "shared") -> tuple[bool, str]:
    if not agent_path.is_file():
        return False, f"Shared agent path is not a file: {agent_path}"

    content = agent_path.read_text(encoding="utf-8")
    frontmatter, error = parse_frontmatter(content)
    if error:
        return False, error

    unexpected_keys = set(frontmatter.keys()) - SHARED_ALLOWED_KEYS
    if unexpected_keys:
        return (
            False,
            "Unexpected key(s) in shared agent frontmatter: "
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

    filename_error = expected_filename(name, mode, agent_path)
    if filename_error:
        return False, f"Filename '{agent_path.name}' must be '{filename_error}'"

    body = body_after_frontmatter(content)
    if not body:
        return False, "Shared agent body cannot be empty"

    for pattern in TOOL_NEUTRALITY_PATTERNS:
        if pattern.search(body):
            return (
                False,
                f"Shared agent body appears tool-specific ({pattern.pattern}). "
                "Move tool-native details into wrappers.",
            )

    label = "Bootstrap shared agent" if mode == "bootstrap_shared" else "Shared agent"
    return True, f"{label} is valid!"


def validate_wrapper_agent(agent_path: Path, *, mode: str = "wrapper") -> tuple[bool, str]:
    if not agent_path.is_file():
        return False, f"Wrapper agent path is not a file: {agent_path}"

    content = agent_path.read_text(encoding="utf-8")
    frontmatter, error = parse_frontmatter(content)
    if error:
        return False, error

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

    filename_error = expected_filename(name, mode, agent_path)
    if filename_error:
        return False, f"Filename '{agent_path.name}' should be '{filename_error}'"

    shared_ref = RELATIVE_SHARED_PATH.format(name=name)
    if shared_ref not in content:
        return False, f"Wrapper body must reference the shared agent path: {shared_ref}"

    if "wrapper" not in content.lower():
        return False, "Wrapper body should identify itself as a tool-specific wrapper"

    if "read that shared file" not in content.lower() and "read the shared file" not in content.lower():
        return (
            False,
            "Wrapper body should instruct the agent to read the shared file before acting",
        )

    body = body_after_frontmatter(content)
    if not body:
        return False, "Wrapper agent body cannot be empty"

    label = "Bootstrap wrapper agent" if mode == "bootstrap_wrapper" else "Wrapper agent"
    return True, f"{label} is valid!"


def validate_agent(agent_path: Path, mode: str | None = None) -> tuple[bool, str]:
    agent_path = Path(agent_path)
    resolved_mode = mode or detect_mode(agent_path)
    if resolved_mode in {"wrapper", "bootstrap_wrapper"}:
        return validate_wrapper_agent(agent_path, mode=resolved_mode)
    return validate_shared_agent(agent_path, mode=resolved_mode)


def check_wrapper_sync(
    wrapper_path: Path,
    agent_name: str,
    shared_description: str,
) -> list[str]:
    messages: list[str] = []
    wrapper_frontmatter, _ = parse_frontmatter(wrapper_path.read_text(encoding="utf-8"))
    if not wrapper_frontmatter:
        return messages

    wrapper_name = wrapper_frontmatter.get("name", "")
    if isinstance(wrapper_name, str) and wrapper_name.strip() != agent_name:
        messages.append(
            f"{wrapper_path}: name '{wrapper_name.strip()}' "
            f"does not match shared agent name '{agent_name}'"
        )

    wrapper_description = wrapper_frontmatter.get("description", "")
    if isinstance(wrapper_description, str) and shared_description:
        if normalize_description(wrapper_description) != shared_description:
            messages.append(f"{wrapper_path}: description does not match shared agent description")

    return messages


def validate_bootstrap_agent(source: Path) -> tuple[bool, list[str]]:
    source = source.resolve()
    messages: list[str] = []
    all_valid = True

    agent_md = source / "AGENT.md"
    valid, message = validate_shared_agent(agent_md, mode="bootstrap_shared")
    messages.append(f"{agent_md}: {message}")
    all_valid = all_valid and valid

    agent_name = ""
    shared_description = ""
    if agent_md.is_file():
        frontmatter, _ = parse_frontmatter(agent_md.read_text(encoding="utf-8"))
        if frontmatter and isinstance(frontmatter.get("name"), str):
            agent_name = frontmatter["name"].strip()
        if frontmatter and isinstance(frontmatter.get("description"), str):
            shared_description = normalize_description(frontmatter["description"])

    wrappers_dir = source / "wrappers"
    if wrappers_dir.is_dir():
        for wrapper_path in sorted(wrappers_dir.glob("*/AGENT.md")):
            valid, message = validate_wrapper_agent(wrapper_path, mode="bootstrap_wrapper")
            messages.append(f"{wrapper_path}: {message}")
            all_valid = all_valid and valid

            if valid and agent_name:
                for sync_error in check_wrapper_sync(wrapper_path, agent_name, shared_description):
                    messages.append(sync_error)
                    all_valid = False

    if all_valid and agent_name:
        messages.append(f"Bootstrap agent '{agent_name}' is valid.")
    return all_valid, messages


def expected_wrapper_tools(root: Path, agent_name: str) -> set[str] | None:
    """Return bootstrap wrapper tools when bootstrap exists; None means require all tools."""
    bootstrap_wrappers = root / "agents" / agent_name / "wrappers"
    if not bootstrap_wrappers.is_dir():
        return None
    return {path.parent.name for path in bootstrap_wrappers.glob("*/AGENT.md")}


def validate_portable_agent(root: Path, name: str) -> tuple[bool, list[str]]:
    root = root.resolve()
    agent_name = name.strip()
    messages: list[str] = []
    all_valid = True

    shared_path = root / ".shared" / "agents" / f"{agent_name}.md"
    valid, message = validate_shared_agent(shared_path)
    messages.append(f"{shared_path}: {message}")
    all_valid = all_valid and valid

    shared_frontmatter: dict | None = None
    shared_description = ""
    if shared_path.is_file():
        shared_frontmatter, _ = parse_frontmatter(shared_path.read_text(encoding="utf-8"))
        if shared_frontmatter and isinstance(shared_frontmatter.get("description"), str):
            shared_description = normalize_description(shared_frontmatter["description"])

    bootstrap_tools = expected_wrapper_tools(root, agent_name)
    required_tools = bootstrap_tools if bootstrap_tools is not None else set(WRAPPER_PATHS.keys())
    validated_wrappers = 0

    for tool, pattern in WRAPPER_PATHS.items():
        if tool not in required_tools:
            continue

        wrapper_path = root / pattern.format(name=agent_name)
        if not wrapper_path.exists():
            all_valid = False
            messages.append(f"{wrapper_path}: Wrapper file not found")
            continue

        valid, message = validate_wrapper_agent(wrapper_path)
        messages.append(f"{wrapper_path}: {message}")
        all_valid = all_valid and valid
        validated_wrappers += 1

        if valid and shared_frontmatter:
            for sync_error in check_wrapper_sync(wrapper_path, agent_name, shared_description):
                messages.append(sync_error)
                all_valid = False

    if all_valid:
        file_count = 1 + validated_wrappers
        messages.append(
            f"Portable agent '{agent_name}' is valid across {file_count} installed file(s)."
        )
    return all_valid, messages


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate a shared or wrapper agent file, or a full portable agent set."
    )
    parser.add_argument(
        "agent_path",
        nargs="?",
        help="Path to a shared or wrapper agent markdown file",
    )
    parser.add_argument(
        "--root",
        help="Repository root when validating a full portable agent set",
    )
    parser.add_argument(
        "--name",
        help="Agent name when validating a full portable agent set (used with --root)",
    )
    parser.add_argument(
        "--mode",
        choices=("shared", "wrapper", "bootstrap_shared", "bootstrap_wrapper"),
        help="Validation mode (auto-detected when omitted)",
    )
    parser.add_argument(
        "--bootstrap-source",
        help="Path to a bootstrap agent directory (agents/<name>/) to validate AGENT.md and wrappers/",
    )
    args = parser.parse_args()

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
