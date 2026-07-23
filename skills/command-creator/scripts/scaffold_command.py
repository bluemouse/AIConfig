#!/usr/bin/env python3
"""
Shared scaffolding helpers for portable slash commands and Copilot prompts.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

from quick_validate import body_after_frontmatter, parse_frontmatter

TOOL_PATHS = {
    "cursor": ".cursor/commands/{name}.md",
    "claude": ".claude/commands/{name}.md",
    "github": ".github/prompts/{name}.prompt.md",
}

SHARED_COMMAND_FILENAME = "COMMAND.md"

DEFAULT_TOOL_FRONTMATTER = {
    "github": {"agent": "agent"},
}


class CommandCreatorError(Exception):
    """Raised for user-correctable errors."""


def slugify_name(value: str) -> str:
    """Normalize a command name to lowercase hyphen-case."""
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    if not value:
        raise CommandCreatorError("Command name cannot be empty after normalization.")
    if len(value) > 64:
        raise CommandCreatorError("Command name must be 64 characters or fewer.")
    return value


def rebuild_frontmatter(frontmatter: dict) -> str:
    yaml_block = yaml.dump(
        frontmatter,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False,
    ).strip()
    return f"---\n{yaml_block}\n---\n"


def frontmatter_block(name: str, description: str, extra: dict | None = None) -> str:
    data = {"name": name, "description": description}
    if extra:
        data.update(extra)
    return rebuild_frontmatter(data)


def normalize_markdown_body(body: str) -> str:
    body = body.strip()
    if not body:
        raise CommandCreatorError("Command body cannot be empty.")
    return body + "\n"


def shared_command_content(name: str, description: str, body: str) -> str:
    return frontmatter_block(name, description) + "\n" + normalize_markdown_body(body)


def merge_frontmatter(
    base: dict,
    overrides: dict | None,
    *,
    locked_keys: tuple[str, ...] = ("name", "description"),
) -> dict:
    merged = dict(base)
    if overrides:
        for key, value in overrides.items():
            if key not in locked_keys:
                merged[key] = value
    for key in locked_keys:
        if key in base:
            merged[key] = base[key]
    return merged


def append_bodies(*parts: str) -> str:
    cleaned = [part.strip() for part in parts if part and part.strip()]
    if not cleaned:
        raise CommandCreatorError("Command body cannot be empty.")
    return "\n\n".join(cleaned) + "\n"


def build_cursor_content(shared_body: str, wrapper_body: str = "") -> str:
    if wrapper_body.strip().startswith("---"):
        raise CommandCreatorError("Cursor command output must not contain YAML frontmatter.")
    return append_bodies(shared_body, wrapper_body)


def build_claude_content(
    name: str,
    description: str,
    shared_body: str,
    wrapper_content: str = "",
    wrapper_frontmatter: dict | None = None,
) -> str:
    base = {"name": name, "description": description}
    merged = merge_frontmatter(base, wrapper_frontmatter)
    wrapper_body = body_after_frontmatter(wrapper_content) if wrapper_content.strip() else ""
    body = append_bodies(shared_body, wrapper_body)
    return rebuild_frontmatter(merged) + "\n" + body


def build_github_content(
    name: str,
    description: str,
    shared_body: str,
    wrapper_content: str = "",
    wrapper_frontmatter: dict | None = None,
) -> str:
    base = {"name": name, "description": description, **DEFAULT_TOOL_FRONTMATTER["github"]}
    merged = merge_frontmatter(base, wrapper_frontmatter)
    wrapper_body = body_after_frontmatter(wrapper_content) if wrapper_content.strip() else ""
    body = append_bodies(shared_body, wrapper_body)
    return rebuild_frontmatter(merged) + "\n" + body


def parse_wrapper_file(path: Path, *, allow_frontmatter: bool) -> tuple[dict | None, str]:
    if not path.is_file():
        return None, ""
    content = path.read_text(encoding="utf-8")
    if not content.strip():
        return None, ""
    if allow_frontmatter:
        frontmatter, error = parse_frontmatter(content)
        if error:
            raise CommandCreatorError(f"Invalid wrapper frontmatter in {path}: {error}")
        return frontmatter, body_after_frontmatter(content)
    if content.strip().startswith("---"):
        raise CommandCreatorError(
            f"Cursor wrapper must not contain YAML frontmatter: {path}"
        )
    return None, content.strip()


def write_file(path: Path, content: str, overwrite: bool) -> None:
    if path.exists() and not overwrite:
        raise CommandCreatorError(f"Refusing to overwrite existing file: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
