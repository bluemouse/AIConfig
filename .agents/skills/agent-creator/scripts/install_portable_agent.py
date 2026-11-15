#!/usr/bin/env python3
"""
Install a bootstrap agent package into the dual-target agent layout.

Reads agents/<name>/AGENT.md and writes two real copies:

- .claude/agents/<name>.md — AGENT.md verbatim (frontmatter + body), which
  Cursor compat-reads.
- .github/agents/<name>.agent.md — a Copilot transform: name/description
  frontmatter plus the body.

Tool-specific guidance belongs in `## Tool notes` sections of the bootstrap
AGENT.md; there is no shared wrapper layer.

Example:
    python install_portable_agent.py \\
        --root . \\
        --name code-reviewer \\
        --source agents/code-reviewer \\
        --overwrite
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import yaml

from create_agent import (
    CLAUDE_AGENT_PATH,
    GITHUB_AGENT_PATH,
    AgentCreatorError,
    slugify_name,
    write_file,
)
from quick_validate import body_after_frontmatter, parse_frontmatter, validate_agent


def read_agent_metadata(agent_md: Path) -> tuple[str, str]:
    if not agent_md.is_file():
        raise AgentCreatorError(f"AGENT.md not found in source: {agent_md}")

    frontmatter, error = parse_frontmatter(agent_md.read_text(encoding="utf-8"))
    if error:
        raise AgentCreatorError(f"Invalid source AGENT.md: {error}")

    description = frontmatter.get("description") or ""
    if not isinstance(description, str):
        raise AgentCreatorError("Source AGENT.md description must be a string.")
    if not description.strip():
        raise AgentCreatorError("Source AGENT.md is missing a description in frontmatter.")

    source_name = frontmatter.get("name") or ""
    if not isinstance(source_name, str):
        raise AgentCreatorError("Source AGENT.md name must be a string.")
    return description.strip(), source_name.strip()


def build_github_content(agent_md_content: str) -> str:
    """Transform an AGENT.md into a GitHub Copilot .agent.md real copy."""
    frontmatter, error = parse_frontmatter(agent_md_content)
    if error or not frontmatter:
        raise AgentCreatorError(f"Cannot build Copilot agent: {error or 'missing frontmatter'}")

    body = body_after_frontmatter(agent_md_content)
    copilot_frontmatter = {
        "name": frontmatter.get("name", ""),
        "description": frontmatter.get("description", ""),
    }
    yaml_block = yaml.dump(
        copilot_frontmatter,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False,
    ).strip()
    rebuilt = f"---\n{yaml_block}\n---\n"
    if body:
        rebuilt += "\n" + body + "\n"
    else:
        rebuilt += "\n"
    return rebuilt


def install_portable_agent(
    root: Path,
    source: Path,
    agent_name: str,
    overwrite: bool,
) -> tuple[list[Path], list[Path]]:
    root = root.resolve()
    source = source.resolve()
    agent_name = slugify_name(agent_name)

    if not source.is_dir():
        raise AgentCreatorError(f"Source directory not found: {source}")

    agent_md = source / "AGENT.md"
    description, source_name = read_agent_metadata(agent_md)
    if source_name and source_name != agent_name:
        raise AgentCreatorError(
            f"Agent name '{agent_name}' does not match source frontmatter name '{source_name}'."
        )

    agent_md_content = agent_md.read_text(encoding="utf-8")
    claude_target = root / CLAUDE_AGENT_PATH.format(name=agent_name)
    github_target = root / GITHUB_AGENT_PATH.format(name=agent_name)

    assert_install_allowed([claude_target, github_target], overwrite)

    write_file(claude_target, agent_md_content, overwrite)
    write_file(github_target, build_github_content(agent_md_content), overwrite)
    written: list[Path] = [claude_target, github_target]

    removed: list[Path] = []
    if overwrite:
        removed = remove_legacy_outputs(root, agent_name)

    return written, removed


def assert_install_allowed(target_paths: list[Path], overwrite: bool) -> None:
    if overwrite:
        return
    for path in target_paths:
        if path.exists():
            raise AgentCreatorError(f"Refusing to overwrite existing file: {path}")


def remove_legacy_outputs(root: Path, agent_name: str) -> list[Path]:
    """Delete legacy shared-layer and wrapper outputs left by older installs."""
    legacy_patterns = {
        "shared": root / ".ai" / "agents" / f"{agent_name}.md",
        "cursor": root / ".cursor" / "agents" / f"{agent_name}.md",
    }
    removed: list[Path] = []
    for stale_path in legacy_patterns.values():
        if stale_path.is_file():
            stale_path.unlink()
            removed.append(stale_path)
    return removed


def validate_install(written: list[Path], validator_script: Path) -> None:
    for path in written:
        valid, message = validate_agent(path)
        if not valid:
            raise AgentCreatorError(f"Validation failed for {path}: {message}")

        result = subprocess.run(
            [sys.executable, str(validator_script), str(path)],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            detail = (result.stdout + result.stderr).strip() or "unknown error"
            raise AgentCreatorError(f"Validation failed for {path}: {detail}")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Install a bootstrap agent into the dual-target agent layout."
    )
    parser.add_argument("--root", required=True, help="Repository root directory.")
    parser.add_argument("--name", required=True, help="Agent name; normalized to hyphen-case.")
    parser.add_argument(
        "--source",
        required=True,
        help="Path to the bootstrap agent directory containing AGENT.md.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        default=True,
        help="Overwrite existing installed agent files (default: true).",
    )
    parser.add_argument(
        "--no-overwrite",
        action="store_false",
        dest="overwrite",
        help="Refuse to overwrite existing install targets.",
    )
    parser.add_argument(
        "--skip-validate",
        action="store_true",
        help="Skip post-install validation (not recommended).",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        written, removed = install_portable_agent(
            root=Path(args.root),
            source=Path(args.source),
            agent_name=args.name,
            overwrite=args.overwrite,
        )
    except AgentCreatorError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if not args.skip_validate:
        validator = Path(__file__).resolve().parent / "quick_validate.py"
        try:
            validate_install(written, validator)
        except AgentCreatorError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1

    print(f"installed {slugify_name(args.name)}:")
    for path in written:
        print(f"- {path}")
    for path in removed:
        print(f"- removed legacy output: {path}")

    print(
        "\nReload VS Code (Copilot) and restart or reload the Claude Code "
        "session so each tool rediscovers the installed agent."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
