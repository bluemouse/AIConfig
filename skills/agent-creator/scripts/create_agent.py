#!/usr/bin/env python3
"""
Create a portable custom agent as two real copies for Claude Code and GitHub Copilot.

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


CLAUDE_AGENT_PATH = ".claude/agents/{name}.md"
GITHUB_AGENT_PATH = ".github/agents/{name}.agent.md"


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


def agent_content(name: str, description: str, instructions: str) -> str:
    return frontmatter(name, description) + "\n" + normalize_markdown_body(instructions)


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
) -> list[Path]:
    root = root.resolve()
    agent_name = slugify_name(name)
    if not description.strip():
        raise AgentCreatorError("Description cannot be empty.")

    content = agent_content(agent_name, description, instructions)

    written: list[Path] = []
    claude_path = root / CLAUDE_AGENT_PATH.format(name=agent_name)
    write_file(claude_path, content, overwrite)
    written.append(claude_path)

    github_path = root / GITHUB_AGENT_PATH.format(name=agent_name)
    write_file(github_path, content, overwrite)
    written.append(github_path)

    return written


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create portable agent files.")
    parser.add_argument("--root", required=True, help="Repository or output root directory.")
    parser.add_argument("--name", required=True, help="Agent name; normalized to hyphen-case.")
    parser.add_argument("--description", required=True, help="Agent trigger description.")
    parser.add_argument(
        "--instructions-file",
        required=True,
        help="Markdown file containing the agent instructions.",
    )
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
