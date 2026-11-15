#!/usr/bin/env python3
"""
Shared scaffolding helpers for portable command-skills.

Commands install as command-skills: a single .agents/skills/<name>/SKILL.md
with `disable-model-invocation: true`, so every coding agent exposes them as
/<name> and the model never self-invokes them.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

from quick_validate import parse_frontmatter


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


def normalize_markdown_body(body: str) -> str:
    body = body.strip()
    if not body:
        raise CommandCreatorError("Command body cannot be empty.")
    return body + "\n"


def command_skill_content(
    name: str,
    description: str,
    body: str,
    allowed_tools: object | None = None,
) -> str:
    """Build the command-skill SKILL.md content.

    Frontmatter carries `disable-model-invocation: true` so the skill is
    slash-invoked only; `allowed-tools` transfers verbatim when declared.
    """
    frontmatter: dict = {
        "name": name,
        "description": description,
        "disable-model-invocation": True,
    }
    if allowed_tools is not None:
        frontmatter["allowed-tools"] = allowed_tools
    return rebuild_frontmatter(frontmatter) + "\n" + normalize_markdown_body(body)


def is_command_skill(skill_md: Path) -> bool:
    """True when the SKILL.md at this path was installed as a command-skill.

    Twin sites (cr-010 — bootstrap layout mandates independent script dirs,
    so this is re-implemented locally; keep the flag semantics identical):
    tools/installer.py:is_command_skill and skills/skill-creator/scripts/
    install_portable_skill.py:is_command_skill.
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


def assert_command_skill_target_available(
    skill_dir: Path,
    skill_md: Path,
    overwrite: bool,
) -> None:
    """Guard the .agents/skills/<name>/ target before any write.

    Commands and skills share one namespace. An existing directory that is
    not a prior command-skill install is a collision and is rejected
    unconditionally (even with --overwrite). A prior command-skill install
    follows normal overwrite semantics so bootstrap edits can be reinstalled.
    """
    if not skill_dir.exists():
        return
    if is_command_skill(skill_md):
        if not overwrite:
            raise CommandCreatorError(
                f"Refusing to overwrite existing command skill: {skill_md}"
            )
        return
    raise CommandCreatorError(
        f"Name collision: skill '{skill_dir.name}' already exists at {skill_dir}. "
        "Commands and skills share the .agents/skills/ namespace; choose a "
        "different command name or remove the existing skill."
    )


def write_file(path: Path, content: str, overwrite: bool) -> None:
    if path.exists() and not overwrite:
        raise CommandCreatorError(f"Refusing to overwrite existing file: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
