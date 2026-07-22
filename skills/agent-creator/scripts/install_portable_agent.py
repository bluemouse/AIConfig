#!/usr/bin/env python3
"""
Install a bootstrap agent package into the portable shared-first layout.

Copies agents/<name>/AGENT.md to .shared/agents/<name>.md and installs
custom tool wrappers from agents/<name>/wrappers/<tool>/AGENT.md when present.

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

from create_agent import TOOL_PATHS, AgentCreatorError, slugify_name, write_file
from quick_validate import body_after_frontmatter, parse_frontmatter, validate_agent


def read_agent_metadata(agent_md: Path) -> tuple[str, str]:
    if not agent_md.is_file():
        raise AgentCreatorError(f"AGENT.md not found in source: {agent_md}")

    frontmatter, error = parse_frontmatter(agent_md.read_text(encoding="utf-8"))
    if error:
        raise AgentCreatorError(f"Invalid source AGENT.md: {error}")

    description = frontmatter.get("description", "").strip()
    if not description:
        raise AgentCreatorError("Source AGENT.md is missing a description in frontmatter.")

    source_name = frontmatter.get("name", "").strip()
    return description, source_name


def sync_description(content: str, description: str) -> str:
    fm, error = parse_frontmatter(content)
    if error or not fm:
        raise AgentCreatorError(f"Cannot sync description: {error or 'missing frontmatter'}")

    name = fm.get("name", "").strip()
    if not name:
        raise AgentCreatorError("Wrapper is missing name in frontmatter")

    updated = dict(fm)
    updated["description"] = description
    body = body_after_frontmatter(content)
    yaml_block = yaml.dump(
        updated,
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


def load_custom_wrapper(source: Path, tool: str, description: str) -> str | None:
    wrapper_path = source / "wrappers" / tool / "AGENT.md"
    if not wrapper_path.is_file():
        return None
    return sync_description(wrapper_path.read_text(encoding="utf-8"), description)


def assert_install_allowed(target_paths: list[Path], overwrite: bool) -> None:
    if overwrite:
        return
    for path in target_paths:
        if path.exists():
            raise AgentCreatorError(f"Refusing to overwrite existing file: {path}")


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

    shared_path = root / ".shared" / "agents" / f"{agent_name}.md"
    shared_content = agent_md.read_text(encoding="utf-8")
    wrapper_installs: list[tuple[str, Path, str]] = []

    for tool, pattern in TOOL_PATHS.items():
        content = load_custom_wrapper(source, tool, description)
        if content is None:
            continue
        wrapper_installs.append((tool, root / pattern.format(name=agent_name), content))

    assert_install_allowed(
        [shared_path, *(path for _, path, _ in wrapper_installs)],
        overwrite,
    )

    write_file(shared_path, shared_content, overwrite)
    written: list[Path] = [shared_path]
    installed_tools: set[str] = set()

    for tool, wrapper_path, content in wrapper_installs:
        write_file(wrapper_path, content, overwrite)
        written.append(wrapper_path)
        installed_tools.add(tool)

    removed: list[Path] = []
    if overwrite:
        for tool, pattern in TOOL_PATHS.items():
            if tool in installed_tools:
                continue
            stale_path = root / pattern.format(name=agent_name)
            if stale_path.is_file():
                stale_path.unlink()
                removed.append(stale_path)

    return written, removed


def validate_install(root: Path, written: list[Path], validator_script: Path) -> None:
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
        description="Install a bootstrap agent into the portable shared-first layout."
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
        help="Overwrite existing shared agent and wrappers (default: true).",
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
            validate_install(Path(args.root), written, validator)
        except AgentCreatorError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1

    print(f"installed {slugify_name(args.name)}:")
    for path in written:
        print(f"- {path}")
    for path in removed:
        print(f"- removed stale wrapper: {path}")

    print(
        "\nReload Cursor, VS Code (Copilot), and Claude Code so each tool "
        "rediscovers the installed agent."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
