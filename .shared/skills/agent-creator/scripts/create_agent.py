#!/usr/bin/env python3
"""
Create a shared custom agent plus tool-specific wrappers for Claude Code,
Cursor, and GitHub Copilot.

Example:
    python create_agent.py \
        --root /path/to/repo \
        --name code-reviewer \
        --description "Reviews code changes before a pull request." \
        --instructions-file /tmp/code-reviewer.md \
        --overwrite
"""

from __future__ import annotations

import argparse
import re
import sys
import textwrap
from pathlib import Path


TOOL_PATHS = {
    "claude": ".claude/agents/{name}.md",
    "cursor": ".cursor/agents/{name}.md",
    "github": ".github/agents/{name}.agent.md",
}

RELATIVE_SHARED_PATH = "../../.shared/agents/{name}.md"

DEFAULT_TOOL_NOTES = {
    "cursor": (
        "Reload the Cursor window after adding or editing this agent "
        "so the agent rediscovers it."
    ),
    "claude": (
        "Restart or reload the Claude Code session after adding or editing "
        "this agent."
    ),
    "github": (
        "Reload VS Code after adding or editing this agent so Copilot "
        "rediscovers it."
    ),
}


class AgentCreatorError(Exception):
    """Raised for user-correctable errors."""


def slugify_name(value: str) -> str:
    """Normalize an agent name to lowercase hyphen-case."""
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    if not value:
        raise AgentCreatorError("Agent name cannot be empty after normalization.")
    if len(value) > 64:
        raise AgentCreatorError("Agent name must be 64 characters or fewer.")
    return value


def yaml_block_value(value: str, indent: int = 2) -> str:
    """Return a YAML folded block scalar for a single string value."""
    cleaned = " ".join(value.strip().split())
    if not cleaned:
        raise AgentCreatorError("Description cannot be empty.")
    wrapped = textwrap.wrap(cleaned, width=88) or [cleaned]
    pad = " " * indent
    return ">-\n" + "\n".join(pad + line for line in wrapped)


def frontmatter(name: str, description: str) -> str:
    return f"---\nname: {name}\ndescription: {yaml_block_value(description)}\n---\n"


def normalize_markdown_body(body: str) -> str:
    body = body.strip()
    if not body:
        raise AgentCreatorError("Instructions file cannot be empty.")
    return body + "\n"


def shared_agent_content(name: str, description: str, instructions: str) -> str:
    return frontmatter(name, description) + "\n" + normalize_markdown_body(instructions)


def wrapper_content(tool: str, name: str, description: str, note: str | None) -> str:
    shared_path = RELATIVE_SHARED_PATH.format(name=name)
    tool_titles = {
        "claude": "Claude Code",
        "cursor": "Cursor",
        "github": "GitHub Copilot",
    }
    title = tool_titles[tool]
    note = (note or DEFAULT_TOOL_NOTES[tool]).strip()

    body = f"""\
# {name} wrapper for {title}

This is a tool-specific wrapper. The canonical shared agent definition is:

`{shared_path}`

Before doing agent work, read that shared file and treat it as the source of truth for the role, task boundaries, review criteria, and response format.

## {title}-specific information

{note}

## Wrapper policy

- Do not treat this wrapper as the full agent specification.
- Prefer the shared file whenever this wrapper and the shared file conflict.
- Keep edits to common behavior in `{shared_path}`.
- Keep only {title}-specific information in this wrapper.
"""
    return frontmatter(name, description) + "\n" + body


def write_file(path: Path, content: str, overwrite: bool) -> None:
    if path.exists() and not overwrite:
        raise AgentCreatorError(f"Refusing to overwrite existing file: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def create_agent(
    root: Path,
    name: str,
    description: str,
    instructions: str,
    overwrite: bool,
    claude_note: str | None = None,
    cursor_note: str | None = None,
    github_note: str | None = None,
) -> list[Path]:
    root = root.resolve()
    agent_name = slugify_name(name)
    if not description.strip():
        raise AgentCreatorError("Description cannot be empty.")

    written: list[Path] = []
    shared_path = root / ".shared" / "agents" / f"{agent_name}.md"
    write_file(shared_path, shared_agent_content(agent_name, description, instructions), overwrite)
    written.append(shared_path)

    notes = {
        "claude": claude_note,
        "cursor": cursor_note,
        "github": github_note,
    }
    for tool, pattern in TOOL_PATHS.items():
        path = root / pattern.format(name=agent_name)
        write_file(path, wrapper_content(tool, agent_name, description, notes[tool]), overwrite)
        written.append(path)

    return written


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create portable shared agent files.")
    parser.add_argument("--root", required=True, help="Repository or output root directory.")
    parser.add_argument("--name", required=True, help="Agent name; normalized to hyphen-case.")
    parser.add_argument("--description", required=True, help="Agent trigger description.")
    parser.add_argument(
        "--instructions-file",
        required=True,
        help="Markdown file containing the shared, tool-neutral agent instructions.",
    )
    parser.add_argument("--claude-note", help="Extra Claude Code-specific wrapper note.")
    parser.add_argument("--cursor-note", help="Extra Cursor-specific wrapper note.")
    parser.add_argument("--github-note", help="Extra GitHub Copilot-specific wrapper note.")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing generated files if they already exist.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        instructions_path = Path(args.instructions_file)
        if not instructions_path.exists():
            raise AgentCreatorError(f"Instructions file not found: {instructions_path}")
        instructions = instructions_path.read_text(encoding="utf-8")
        written = create_agent(
            root=Path(args.root),
            name=args.name,
            description=args.description,
            instructions=instructions,
            overwrite=args.overwrite,
            claude_note=args.claude_note,
            cursor_note=args.cursor_note,
            github_note=args.github_note,
        )
    except AgentCreatorError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print("created agent files:")
    for path in written:
        print(f"- {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
