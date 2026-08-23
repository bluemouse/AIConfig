#!/usr/bin/env python3
"""
Install or uninstall portable skills, agents, and commands from this repo into another project.

Copies the shared-first layout (.ai/ plus tool wrappers under .cursor/, .claude/,
.github/) from AIConfig into a target project root.

Examples:
    python tools/installer.py /path/to/other-project
    python tools/installer.py /path/to/other-project --skills cpp-coding vulkan-dev
    python tools/installer.py /path/to/other-project --commands git-commit
    python tools/installer.py /path/to/other-project --bundles core-dev-workflow
    python tools/installer.py /path/to/other-project --bundles extended-dev-workflow --override
    python tools/installer.py /path/to/other-project --bundles core-dev-workflow --skills cpp-coding
    python tools/installer.py /path/to/other-project --bundles target-bundle
    python tools/installer.py /path/to/other-project --dev-workflow
    python tools/installer.py /path/to/other-project --dev-workflow --uninstall
    python tools/installer.py /path/to/other-project --agents my-agent --uninstall
    python tools/installer.py /path/to/other-project --commands git-commit --uninstall
    python tools/installer.py   # GUI when no arguments
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import tkinter as tk
import yaml
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, ttk
from typing import Literal

REPO_ROOT = Path(__file__).resolve().parent.parent

SHARED_SKILL_DIR = ".ai/skills/{name}"
SHARED_AGENT_FILE = ".ai/agents/{name}.md"
SHARED_COMMAND_FILE = ".ai/commands/{name}.md"
SHARED_SCRIPTS_DIR = ".ai/tools/{name}"

TOOL_SKILL_DIRS = {
    "cursor": ".cursor/skills/{name}",
    "claude": ".claude/skills/{name}",
    "github": ".github/skills/{name}",
}

TOOL_AGENT_FILES = {
    "cursor": ".cursor/agents/{name}.md",
    "claude": ".claude/agents/{name}.md",
    "github": ".github/agents/{name}.agent.md",
}

TOOL_COMMAND_FILES = {
    "cursor": ".cursor/commands/{name}.md",
    "claude": ".claude/commands/{name}.md",
    "github": ".github/prompts/{name}.prompt.md",
}

# Scripts are directory trees under .ai/tools/<name>/ (no tool wrappers).
TOOL_SCRIPTS_SCAN_REL_DIRS = (".ai/tools",)

TOOL_SKILL_SCAN_REL_DIRS = (
    ".cursor/skills",
    ".claude/skills",
    ".github/skills",
)

TOOL_AGENT_SCAN_REL_DIRS = (
    (".cursor/agents", ".md"),
    (".claude/agents", ".md"),
    (".github/agents", ".agent.md"),
)

TOOL_COMMAND_SCAN_REL_DIRS = (
    (".cursor/commands", ".md"),
    (".claude/commands", ".md"),
    (".github/prompts", ".prompt.md"),
)

# Scripts are discovered as subdirectories of tools/ in the repo root.
# A scripts "name" is the directory name under tools/.

SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

RELOAD_REMINDER = (
    "Reload Cursor, VS Code (Copilot), and Claude Code so each tool "
    "rediscovers the installed skills, agents, and commands."
)

BUNDLES_JSON = Path(__file__).resolve().parent / "bundles.json"

TARGET_BUNDLE_ID = "target-bundle"
TARGET_BUNDLE_NAME = "Target bundle"
TARGET_BUNDLE_DESCRIPTION = (
    "Skills, agents, commands, and scripts currently installed in the selected "
    "target project (matching this AIConfig catalog)."
)

# Dev-workflow harness: the orchestrator plus all phase doer/checker skills,
# the dev-workflow command, and the validation scripts tree. Installed/
# uninstalled together via the dev-workflow-harness bundle (and the
# --dev-workflow CLI alias).
DEV_WORKFLOW_SKILLS = (
    "dev-workflow-orchestrator",
    "prompt-clarifier",
    "research-guide",
    "research-reviewer",
    "plan-guide",
    "plan-reviewer",
    "plan-executor",
    "implementation-auditor",
    "finding-resolver",
    "code-reviewer",
    "commit-message-writer",
)
DEV_WORKFLOW_COMMANDS = ("dev-workflow",)
DEV_WORKFLOW_SCRIPTS = ("dev-workflow",)

BundleSelectionState = Literal["all", "none", "partial"]


class InstallerError(Exception):
    """Raised for user-correctable errors."""


@dataclass(frozen=True)
class Bundle:
    id: str
    name: str
    description: str
    skills: frozenset[str]
    agents: frozenset[str] = frozenset()
    commands: frozenset[str] = frozenset()
    scripts: frozenset[str] = frozenset()

    @property
    def is_empty(self) -> bool:
        """Return True if the bundle has no members of any kind."""
        return not (self.skills or self.agents or self.commands or self.scripts)


# Backward-compatible alias.
SkillBundle = Bundle


def bundle_selection_state(
    members: Sequence[str],
    selected: Callable[[str], bool],
) -> BundleSelectionState:
    """Return whether all, none, or some bundle members are selected."""
    if not members:
        return "none"
    selected_count = sum(1 for name in members if selected(name))
    if selected_count == 0:
        return "none"
    if selected_count == len(members):
        return "all"
    return "partial"


def bundle_toggle_target_state(current: BundleSelectionState) -> bool:
    """Return the selection value to apply when a bundle toggle is clicked."""
    return current != "all"


def format_selection_help(
    entries: Sequence[tuple[str, str]],
    *,
    empty_message: str,
) -> str:
    """Format selected item names and descriptions for the Help window."""
    if not entries:
        return empty_message

    blocks: list[str] = []
    for name, description in entries:
        body = description.strip() or "(No description available.)"
        underline = "=" * len(name)
        blocks.append(f"{name}\n{underline}\n{body}")
    return "\n\n".join(blocks) + "\n"


def bundle_help_entries(
    bundles: Sequence[Bundle],
    *,
    present_members: Callable[[Bundle], Sequence[str]],
    is_selected: Callable[[str], bool],
) -> list[tuple[str, str]]:
    """Return display name and description tuples for bundles with any selected members."""
    entries: list[tuple[str, str]] = []
    for bundle in bundles:
        members = present_members(bundle)
        state = bundle_selection_state(members, is_selected)
        if state == "none":
            continue
        display_name = bundle.name if state == "all" else f"{bundle.name} (partial)"
        entries.append((display_name, bundle.description))
    return entries


@dataclass
class OperationResult:
    installed: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    removed: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def slugify_name(value: str) -> str:
    """Normalize and validate a skill, agent, or command slug."""
    normalized = value.strip().lower()
    normalized = re.sub(r"[^a-z0-9]+", "-", normalized)
    normalized = re.sub(r"-+", "-", normalized).strip("-")
    if not normalized:
        raise InstallerError("Name cannot be empty after normalization.")
    if len(normalized) > 64:
        raise InstallerError("Name must be 64 characters or fewer.")
    if not SLUG_PATTERN.fullmatch(normalized):
        raise InstallerError(f"Invalid name: {value!r}")
    return normalized


def load_skill_bundles(path: Path = BUNDLES_JSON) -> list[Bundle]:
    """Load workflow bundles from bundles.json.

    Each bundle may define any combination of skills, agents, commands, and
    scripts. Bases are reusable member sets keyed by id; a base may also carry
    any combination of the four member types.
    """
    if not path.is_file():
        raise InstallerError(f"Bundle config not found: {path}")

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise InstallerError(f"Invalid bundle config {path}: {exc}") from exc

    if not isinstance(payload, dict):
        raise InstallerError(f"Invalid bundle config {path}: root must be an object.")

    base_registry = _load_bundle_base_registry(path, payload.get("bases"))

    raw_bundles = payload.get("bundles")
    if not isinstance(raw_bundles, list) or not raw_bundles:
        raise InstallerError(f"Invalid bundle config {path}: 'bundles' must be a non-empty list.")

    bundles: list[Bundle] = []
    seen_ids: set[str] = set()
    for index, entry in enumerate(raw_bundles):
        if not isinstance(entry, dict):
            raise InstallerError(
                f"Invalid bundle config {path}: bundles[{index}] must be an object."
            )

        missing = [key for key in ("id", "name", "description") if key not in entry]
        if missing:
            raise InstallerError(
                f"Invalid bundle config {path}: bundles[{index}] missing keys: {', '.join(missing)}"
            )

        bundle_id = slugify_name(str(entry["id"]))
        if bundle_id in seen_ids:
            raise InstallerError(f"Invalid bundle config {path}: duplicate bundle id {bundle_id!r}.")
        seen_ids.add(bundle_id)

        resolved_skills: set[str] = set()
        resolved_agents: set[str] = set()
        resolved_commands: set[str] = set()
        resolved_scripts: set[str] = set()

        raw_bundle_bases = entry.get("bases", [])
        if raw_bundle_bases is None:
            raw_bundle_bases = []
        if not isinstance(raw_bundle_bases, list):
            raise InstallerError(
                f"Invalid bundle config {path}: bundles[{index}] bases must be a list."
            )
        for base_id in raw_bundle_bases:
            base_key = slugify_name(str(base_id))
            if base_key not in base_registry:
                raise InstallerError(
                    f"Invalid bundle config {path}: bundles[{index}] references unknown base {base_key!r}."
                )
            base = base_registry[base_key]
            resolved_skills.update(base.skills)
            resolved_agents.update(base.agents)
            resolved_commands.update(base.commands)
            resolved_scripts.update(base.scripts)

        resolved_skills.update(_parse_member_list(entry, "skills", path, index))
        resolved_agents.update(_parse_member_list(entry, "agents", path, index))
        resolved_commands.update(_parse_member_list(entry, "commands", path, index))
        resolved_scripts.update(_parse_member_list(entry, "scripts", path, index))

        if not (resolved_skills or resolved_agents or resolved_commands or resolved_scripts):
            raise InstallerError(
                f"Invalid bundle config {path}: bundles[{index}] resolved to an empty bundle."
            )

        bundles.append(
            Bundle(
                id=bundle_id,
                name=str(entry["name"]).strip(),
                description=str(entry["description"]).strip(),
                skills=frozenset(resolved_skills),
                agents=frozenset(resolved_agents),
                commands=frozenset(resolved_commands),
                scripts=frozenset(resolved_scripts),
            )
        )

    return bundles


def _parse_member_list(
    entry: dict,
    key: str,
    path: Path,
    index: int,
) -> set[str]:
    """Parse an optional member list (skills/agents/commands/scripts) from a bundle/base entry."""
    if key not in entry:
        return set()
    raw = entry[key]
    if not isinstance(raw, list):
        raise InstallerError(
            f"Invalid bundle config {path}: bundles[{index}] {key} must be a list."
        )
    return {slugify_name(str(name)) for name in raw}


def _load_bundle_base_registry(path: Path, raw_bases: object) -> dict[str, Bundle]:
    """Parse the top-level bases registry from bundles.json.

    A base is a reusable member set. It must define at least one of skills,
    agents, commands, or scripts. For backward compatibility, a base with only
    a ``skills`` key is valid.
    """
    if raw_bases is None:
        return {}
    if not isinstance(raw_bases, list):
        raise InstallerError(f"Invalid bundle config {path}: 'bases' must be a list.")

    base_registry: dict[str, Bundle] = {}
    for index, entry in enumerate(raw_bases):
        if not isinstance(entry, dict):
            raise InstallerError(
                f"Invalid bundle config {path}: bases[{index}] must be an object."
            )

        if "id" not in entry:
            raise InstallerError(
                f"Invalid bundle config {path}: bases[{index}] missing keys: id"
            )

        base_id = slugify_name(str(entry["id"]))
        if base_id in base_registry:
            raise InstallerError(f"Invalid bundle config {path}: duplicate base id {base_id!r}.")

        skills = frozenset(_parse_member_list(entry, "skills", path, index))
        agents = frozenset(_parse_member_list(entry, "agents", path, index))
        commands = frozenset(_parse_member_list(entry, "commands", path, index))
        scripts = frozenset(_parse_member_list(entry, "scripts", path, index))

        if not (skills or agents or commands or scripts):
            raise InstallerError(
                f"Invalid bundle config {path}: bases[{index}] must define at least one of "
                "skills, agents, commands, or scripts."
            )

        base_registry[base_id] = Bundle(
            id=base_id,
            name=base_id,
            description="",
            skills=skills,
            agents=agents,
            commands=commands,
            scripts=scripts,
        )

    return base_registry


def normalize_names(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        slug = slugify_name(value)
        if slug not in seen:
            seen.add(slug)
            ordered.append(slug)
    return ordered


def known_bundle_ids(path: Path = BUNDLES_JSON) -> list[str]:
    """Return sorted bundle ids from bundles.json plus the dynamic target bundle."""
    return sorted({bundle.id for bundle in load_skill_bundles(path)} | {TARGET_BUNDLE_ID})


@dataclass
class BundleSelection:
    """Resolved members of one or more bundles, grouped by kind."""

    skills: list[str] = field(default_factory=list)
    agents: list[str] = field(default_factory=list)
    commands: list[str] = field(default_factory=list)
    scripts: list[str] = field(default_factory=list)

    def extend(self, other: "BundleSelection") -> None:
        self.skills.extend(other.skills)
        self.agents.extend(other.agents)
        self.commands.extend(other.commands)
        self.scripts.extend(other.scripts)

    def dedupe(self) -> None:
        self.skills = normalize_names(self.skills)
        self.agents = normalize_names(self.agents)
        self.commands = normalize_names(self.commands)
        self.scripts = normalize_names(self.scripts)

    @property
    def is_empty(self) -> bool:
        return not (self.skills or self.agents or self.commands or self.scripts)


def resolve_bundle(
    bundle_ids: Sequence[str],
    *,
    path: Path = BUNDLES_JSON,
    target_root: Path | None = None,
) -> BundleSelection:
    """Resolve bundle ids from bundles.json into a grouped member selection."""
    bundles = load_skill_bundles(path)
    by_id = {bundle.id: bundle for bundle in bundles}
    normalized_bundle_ids = normalize_names(bundle_ids)
    selection = BundleSelection()
    for raw_id in bundle_ids:
        bundle_id = slugify_name(str(raw_id))
        if bundle_id == TARGET_BUNDLE_ID:
            if target_root is None:
                raise InstallerError("Target bundle requires a target project path.")
            target_bundle = build_target_bundle(target_root)
            if target_bundle.is_empty and normalized_bundle_ids == [TARGET_BUNDLE_ID]:
                raise InstallerError(
                    "Target bundle: no matching installed members found in target project."
                )
            selection.extend(BundleSelection(
                skills=sorted(target_bundle.skills),
                agents=sorted(target_bundle.agents),
                commands=sorted(target_bundle.commands),
                scripts=sorted(target_bundle.scripts),
            ))
            continue
        if bundle_id not in by_id:
            known = ", ".join(known_bundle_ids(path))
            raise InstallerError(
                f"Unknown bundle {bundle_id!r}. Known bundles: {known}"
            )
        bundle = by_id[bundle_id]
        selection.extend(BundleSelection(
            skills=sorted(bundle.skills),
            agents=sorted(bundle.agents),
            commands=sorted(bundle.commands),
            scripts=sorted(bundle.scripts),
        ))
    selection.dedupe()
    return selection


def resolve_bundle_skills(
    bundle_ids: Sequence[str],
    *,
    path: Path = BUNDLES_JSON,
    target_root: Path | None = None,
) -> list[str]:
    """Resolve bundle ids from bundles.json into a deduplicated skill list.

    Backward-compatible wrapper around resolve_bundle for callers that only
    need skills.
    """
    return resolve_bundle(bundle_ids, path=path, target_root=target_root).skills


def resolve_cli_selection(
    *,
    bundle_ids: Sequence[str] | None,
    skill_names: Sequence[str] | None,
    agent_names: Sequence[str] | None,
    command_names: Sequence[str] | None,
    script_names: Sequence[str] | None,
    target_root: Path | None = None,
) -> BundleSelection:
    """Resolve CLI selection from bundles, explicit names, or all discovered items."""
    selection = BundleSelection()
    if bundle_ids:
        selection.extend(resolve_bundle(bundle_ids, target_root=target_root))
    if skill_names:
        selection.skills.extend(normalize_names(skill_names))
    if agent_names:
        selection.agents.extend(normalize_names(agent_names))
    if command_names:
        selection.commands.extend(normalize_names(command_names))
    if script_names:
        selection.scripts.extend(normalize_names(script_names))
    if bundle_ids or skill_names or agent_names or command_names or script_names:
        selection.dedupe()
        return selection
    # No explicit selection: default to all discovered items.
    return BundleSelection(
        skills=discover_skills(),
        agents=discover_agents(),
        commands=discover_commands(),
        scripts=discover_scripts(),
    )


def resolve_cli_skills(
    *,
    bundle_ids: Sequence[str] | None,
    skill_names: Sequence[str] | None,
    target_root: Path | None = None,
) -> list[str]:
    """Resolve CLI skill selection from bundles, explicit names, or all discovered skills.

    Backward-compatible wrapper around resolve_cli_selection for callers that
    only need skills.
    """
    return resolve_cli_selection(
        bundle_ids=bundle_ids,
        skill_names=skill_names,
        agent_names=None,
        command_names=None,
        script_names=None,
        target_root=target_root,
    ).skills


def discover_skills_in_project(project_root: Path) -> list[str]:
    """Return skill slugs installed under project_root/.ai/skills/."""
    names: set[str] = set()
    shared_root = project_root / ".ai" / "skills"
    if not shared_root.is_dir():
        return []
    for child in shared_root.iterdir():
        if child.is_dir() and (child / "SKILL.md").is_file():
            names.add(child.name)
    return sorted(names)


def discover_agents_in_project(project_root: Path) -> list[str]:
    """Return agent slugs installed under project_root/.ai/agents/."""
    names: set[str] = set()
    shared_root = project_root / ".ai" / "agents"
    if not shared_root.is_dir():
        return []
    for child in shared_root.iterdir():
        if child.is_file() and child.suffix == ".md" and not child.name.startswith("."):
            names.add(child.stem)
    return sorted(names)


def discover_commands_in_project(project_root: Path) -> list[str]:
    """Return command slugs installed under project_root/.ai/commands/."""
    names: set[str] = set()
    shared_root = project_root / ".ai" / "commands"
    if not shared_root.is_dir():
        return []
    for child in shared_root.iterdir():
        if child.is_file() and child.suffix == ".md" and not child.name.startswith("."):
            names.add(child.stem)
    return sorted(names)


def discover_scripts_in_project(project_root: Path) -> list[str]:
    """Return scripts directory names installed under project_root/.ai/tools/."""
    names: set[str] = set()
    shared_root = project_root / ".ai" / "tools"
    if not shared_root.is_dir():
        return []
    for child in shared_root.iterdir():
        if child.is_dir() and not child.name.startswith(".") and not child.name.startswith("__"):
            names.add(child.name)
    return sorted(names)


def build_target_bundle(
    target_root: Path,
    *,
    available_skills: Sequence[str] | None = None,
    available_agents: Sequence[str] | None = None,
    available_commands: Sequence[str] | None = None,
    available_scripts: Sequence[str] | None = None,
) -> Bundle:
    """Build the dynamic target bundle from installed members in the target project.

    Membership for each kind is the intersection of what is installed in the
    target project's shared ``.ai/`` layer and what is available in this
    AIConfig repository catalog.
    """
    if available_skills is None:
        available_skills = discover_skills()
    if available_agents is None:
        available_agents = discover_agents()
    if available_commands is None:
        available_commands = discover_commands()
    if available_scripts is None:
        available_scripts = discover_scripts()

    def _intersect(
        installed: Sequence[str], available: Sequence[str]
    ) -> frozenset[str]:
        available_set = set(available)
        return frozenset(name for name in installed if name in available_set)

    return Bundle(
        id=TARGET_BUNDLE_ID,
        name=TARGET_BUNDLE_NAME,
        description=TARGET_BUNDLE_DESCRIPTION,
        skills=_intersect(discover_skills_in_project(target_root), available_skills),
        agents=_intersect(discover_agents_in_project(target_root), available_agents),
        commands=_intersect(discover_commands_in_project(target_root), available_commands),
        scripts=_intersect(discover_scripts_in_project(target_root), available_scripts),
    )


def resolve_target_bundle_skills(target_root: Path) -> list[str]:
    """Return sorted skills for the dynamic target bundle."""
    return sorted(build_target_bundle(target_root).skills)


def discover_skills() -> list[str]:
    names: set[str] = set()
    for rel_dir in TOOL_SKILL_SCAN_REL_DIRS:
        scan_root = REPO_ROOT / rel_dir
        if not scan_root.is_dir():
            continue
        for child in scan_root.iterdir():
            if child.is_dir() and (child / "SKILL.md").is_file():
                names.add(child.name)
    return sorted(names)


def discover_agents() -> list[str]:
    names: set[str] = set()
    for rel_dir, suffix in TOOL_AGENT_SCAN_REL_DIRS:
        scan_root = REPO_ROOT / rel_dir
        if not scan_root.is_dir():
            continue
        for child in scan_root.iterdir():
            if not child.is_file() or child.name.startswith("."):
                continue
            if suffix == ".agent.md" and child.name.endswith(".agent.md"):
                names.add(child.name[: -len(".agent.md")])
            elif suffix == ".md" and child.suffix == ".md" and not child.name.endswith(".agent.md"):
                names.add(child.stem)
    return sorted(names)


def discover_commands() -> list[str]:
    names: set[str] = set()
    for rel_dir, suffix in TOOL_COMMAND_SCAN_REL_DIRS:
        scan_root = REPO_ROOT / rel_dir
        if not scan_root.is_dir():
            continue
        for child in scan_root.iterdir():
            if not child.is_file() or child.name.startswith("."):
                continue
            if suffix == ".prompt.md" and child.name.endswith(".prompt.md"):
                names.add(child.name[: -len(".prompt.md")])
            elif suffix == ".md" and child.suffix == ".md" and not child.name.endswith(".prompt.md"):
                names.add(child.stem)
    return sorted(names)


def parse_frontmatter(content: str) -> dict | None:
    """Parse YAML frontmatter from a skill or agent markdown file."""
    if not content.startswith("---"):
        return None

    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return None

    try:
        frontmatter = yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return None

    if not isinstance(frontmatter, dict):
        return None

    return frontmatter


def read_description_from_markdown(path: Path) -> str | None:
    """Return the frontmatter description from a markdown file, if present."""
    if not path.is_file():
        return None

    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return None

    frontmatter = parse_frontmatter(content)
    if frontmatter is None:
        return None

    description = frontmatter.get("description")
    if not isinstance(description, str):
        return None

    stripped = description.strip()
    return stripped or None


def load_skill_descriptions(names: Sequence[str]) -> dict[str, str]:
    """Map skill slugs to descriptions from shared SKILL.md frontmatter."""
    descriptions: dict[str, str] = {}
    for name in names:
        path = REPO_ROOT / ".ai/skills" / name / "SKILL.md"
        description = read_description_from_markdown(path)
        if description is not None:
            descriptions[name] = description
    return descriptions


def load_agent_descriptions(names: Sequence[str]) -> dict[str, str]:
    """Map agent slugs to descriptions from shared agent markdown frontmatter."""
    descriptions: dict[str, str] = {}
    for name in names:
        path = REPO_ROOT / ".ai/agents" / f"{name}.md"
        description = read_description_from_markdown(path)
        if description is not None:
            descriptions[name] = description
    return descriptions


def load_command_descriptions(names: Sequence[str]) -> dict[str, str]:
    """Map command slugs to descriptions from shared command markdown frontmatter."""
    descriptions: dict[str, str] = {}
    for name in names:
        path = REPO_ROOT / ".ai/commands" / f"{name}.md"
        description = read_description_from_markdown(path)
        if description is not None:
            descriptions[name] = description
    return descriptions


def discover_scripts() -> list[str]:
    """Return scripts directory names discovered under REPO_ROOT/.ai/tools/."""
    names: set[str] = set()
    for rel_dir in TOOL_SCRIPTS_SCAN_REL_DIRS:
        scan_root = REPO_ROOT / rel_dir
        if not scan_root.is_dir():
            continue
        for child in scan_root.iterdir():
            if child.is_dir() and not child.name.startswith(".") and not child.name.startswith("__"):
                names.add(child.name)
    return sorted(names)


def load_scripts_descriptions(names: Sequence[str]) -> dict[str, str]:
    """Map scripts names to a short description.

    Scripts directories do not carry frontmatter; the description is derived
    from a README.md in the directory if present, otherwise the name itself.
    """
    descriptions: dict[str, str] = {}
    for name in names:
        readme = REPO_ROOT / ".ai" / "tools" / name / "README.md"
        if readme.is_file():
            try:
                text = readme.read_text(encoding="utf-8").strip()
                first_line = text.splitlines()[0].lstrip("# ").strip() if text else ""
                descriptions[name] = first_line or f"Scripts directory: {name}"
            except OSError:
                descriptions[name] = f"Scripts directory: {name}"
        else:
            descriptions[name] = f"Scripts directory: {name}"
    return descriptions


def validate_target(source: Path, target: Path, *, create: bool) -> Path:
    target = target.resolve()
    source = source.resolve()
    if target == source:
        raise InstallerError("Target cannot be the AIConfig repository root.")
    if source in target.parents:
        raise InstallerError(
            "Target cannot be inside the AIConfig repository "
            f"({target} is under {source})."
        )
    if not target.exists():
        if create:
            target.mkdir(parents=True, exist_ok=True)
        return target
    if not target.is_dir():
        raise InstallerError(f"Target is not a directory: {target}")
    return target


def format_rel(path: Path, base: Path) -> str:
    try:
        return str(path.relative_to(base))
    except ValueError:
        return str(path)


def skill_copy_pairs(source_root: Path, target_root: Path, name: str) -> list[tuple[Path, Path]]:
    pairs: list[tuple[Path, Path]] = []
    shared_src = source_root / SHARED_SKILL_DIR.format(name=name)
    shared_dest = target_root / SHARED_SKILL_DIR.format(name=name)
    pairs.append((shared_src, shared_dest))
    for rel_template in TOOL_SKILL_DIRS.values():
        src = source_root / rel_template.format(name=name)
        if src.exists():
            pairs.append((src, target_root / rel_template.format(name=name)))
    return pairs


def agent_copy_pairs(source_root: Path, target_root: Path, name: str) -> list[tuple[Path, Path]]:
    pairs: list[tuple[Path, Path]] = []
    shared_src = source_root / SHARED_AGENT_FILE.format(name=name)
    shared_dest = target_root / SHARED_AGENT_FILE.format(name=name)
    pairs.append((shared_src, shared_dest))
    for rel_template in TOOL_AGENT_FILES.values():
        src = source_root / rel_template.format(name=name)
        if src.exists():
            pairs.append((src, target_root / rel_template.format(name=name)))
    return pairs


def skill_remove_paths(target_root: Path, name: str) -> list[Path]:
    paths = [target_root / SHARED_SKILL_DIR.format(name=name)]
    for rel_template in TOOL_SKILL_DIRS.values():
        paths.append(target_root / rel_template.format(name=name))
    return paths


def agent_remove_paths(target_root: Path, name: str) -> list[Path]:
    paths = [target_root / SHARED_AGENT_FILE.format(name=name)]
    for rel_template in TOOL_AGENT_FILES.values():
        paths.append(target_root / rel_template.format(name=name))
    return paths


def command_copy_pairs(source_root: Path, target_root: Path, name: str) -> list[tuple[Path, Path]]:
    pairs: list[tuple[Path, Path]] = []
    shared_src = source_root / SHARED_COMMAND_FILE.format(name=name)
    shared_dest = target_root / SHARED_COMMAND_FILE.format(name=name)
    pairs.append((shared_src, shared_dest))
    for rel_template in TOOL_COMMAND_FILES.values():
        src = source_root / rel_template.format(name=name)
        if src.exists():
            pairs.append((src, target_root / rel_template.format(name=name)))
    return pairs


def command_remove_paths(target_root: Path, name: str) -> list[Path]:
    paths = [target_root / SHARED_COMMAND_FILE.format(name=name)]
    for rel_template in TOOL_COMMAND_FILES.values():
        paths.append(target_root / rel_template.format(name=name))
    return paths


def scripts_copy_pairs(source_root: Path, target_root: Path, name: str) -> list[tuple[Path, Path]]:
    """Return (src, dest) pairs for a scripts directory tree under tools/<name>/."""
    src = source_root / SHARED_SCRIPTS_DIR.format(name=name)
    dest = target_root / SHARED_SCRIPTS_DIR.format(name=name)
    return [(src, dest)]


def scripts_remove_paths(target_root: Path, name: str) -> list[Path]:
    return [target_root / SHARED_SCRIPTS_DIR.format(name=name)]


def remove_path(path: Path) -> None:
    if path.is_dir():
        shutil.rmtree(path)
    elif path.is_file():
        path.unlink()


def copy_path(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if src.is_dir():
        shutil.copytree(src, dest)
    elif src.is_file():
        shutil.copy2(src, dest)
    else:
        raise InstallerError(f"Source path does not exist: {src}")


def install_items(
    *,
    source_root: Path,
    target_root: Path,
    skills: Sequence[str],
    agents: Sequence[str],
    commands: Sequence[str],
    scripts: Sequence[str] = (),
    override: bool = False,
) -> OperationResult:
    result = OperationResult()
    target_root = validate_target(source_root, target_root, create=True)

    for name in skills:
        slug = slugify_name(name)
        pairs = skill_copy_pairs(source_root, target_root, slug)
        shared_src = pairs[0][0]
        if not shared_src.is_dir():
            result.errors.append(
                f"skill {slug}: missing shared source {format_rel(shared_src, source_root)}"
            )
            continue

        for src, dest in pairs:
            rel_dest = format_rel(dest, target_root)
            if dest.exists():
                if not override:
                    result.skipped.append(rel_dest)
                    continue
                remove_path(dest)
            try:
                copy_path(src, dest)
                result.installed.append(rel_dest)
            except OSError as exc:
                result.errors.append(f"{rel_dest}: {exc}")

    for name in agents:
        slug = slugify_name(name)
        pairs = agent_copy_pairs(source_root, target_root, slug)
        shared_src = pairs[0][0]
        if not shared_src.is_file():
            result.errors.append(
                f"agent {slug}: missing shared source {format_rel(shared_src, source_root)}"
            )
            continue

        for src, dest in pairs:
            rel_dest = format_rel(dest, target_root)
            if dest.exists():
                if not override:
                    result.skipped.append(rel_dest)
                    continue
                remove_path(dest)
            try:
                copy_path(src, dest)
                result.installed.append(rel_dest)
            except OSError as exc:
                result.errors.append(f"{rel_dest}: {exc}")

    for name in commands:
        slug = slugify_name(name)
        pairs = command_copy_pairs(source_root, target_root, slug)
        shared_src = pairs[0][0]
        if not shared_src.is_file():
            result.errors.append(
                f"command {slug}: missing shared source {format_rel(shared_src, source_root)}"
            )
            continue

        for src, dest in pairs:
            rel_dest = format_rel(dest, target_root)
            if dest.exists():
                if not override:
                    result.skipped.append(rel_dest)
                    continue
                remove_path(dest)
            try:
                copy_path(src, dest)
                result.installed.append(rel_dest)
            except OSError as exc:
                result.errors.append(f"{rel_dest}: {exc}")

    for name in scripts:
        slug = slugify_name(name)
        pairs = scripts_copy_pairs(source_root, target_root, slug)
        shared_src = pairs[0][0]
        if not shared_src.is_dir():
            result.errors.append(
                f"scripts {slug}: missing source {format_rel(shared_src, source_root)}"
            )
            continue

        for src, dest in pairs:
            rel_dest = format_rel(dest, target_root)
            if dest.exists():
                if not override:
                    result.skipped.append(rel_dest)
                    continue
                remove_path(dest)
            try:
                copy_path(src, dest)
                result.installed.append(rel_dest)
            except OSError as exc:
                result.errors.append(f"{rel_dest}: {exc}")

    return result


def uninstall_items(
    *,
    target_root: Path,
    skills: Sequence[str],
    agents: Sequence[str],
    commands: Sequence[str],
    scripts: Sequence[str] = (),
) -> OperationResult:
    result = OperationResult()
    target_root = validate_target(REPO_ROOT, target_root, create=False)
    if not target_root.exists():
        return result

    for name in skills:
        slug = slugify_name(name)
        for path in skill_remove_paths(target_root, slug):
            if path.exists():
                try:
                    remove_path(path)
                    result.removed.append(format_rel(path, target_root))
                except OSError as exc:
                    result.errors.append(f"{format_rel(path, target_root)}: {exc}")

    for name in agents:
        slug = slugify_name(name)
        for path in agent_remove_paths(target_root, slug):
            if path.exists():
                try:
                    remove_path(path)
                    result.removed.append(format_rel(path, target_root))
                except OSError as exc:
                    result.errors.append(f"{format_rel(path, target_root)}: {exc}")

    for name in commands:
        slug = slugify_name(name)
        for path in command_remove_paths(target_root, slug):
            if path.exists():
                try:
                    remove_path(path)
                    result.removed.append(format_rel(path, target_root))
                except OSError as exc:
                    result.errors.append(f"{format_rel(path, target_root)}: {exc}")

    for name in scripts:
        slug = slugify_name(name)
        for path in scripts_remove_paths(target_root, slug):
            if path.exists():
                try:
                    remove_path(path)
                    result.removed.append(format_rel(path, target_root))
                except OSError as exc:
                    result.errors.append(f"{format_rel(path, target_root)}: {exc}")

    return result


def format_result(result: OperationResult, *, uninstall: bool) -> str:
    lines: list[str] = []
    if uninstall:
        if result.removed:
            lines.append("Removed:")
            lines.extend(f"  - {path}" for path in result.removed)
        else:
            lines.append("Removed: (nothing matched)")
    else:
        if result.installed:
            lines.append("Installed:")
            lines.extend(f"  - {path}" for path in result.installed)
        if result.skipped:
            lines.append("Skipped (already exists; use --override to replace):")
            lines.extend(f"  - {path}" for path in result.skipped)
        if not result.installed and not result.skipped:
            lines.append("Installed: (nothing copied)")

    if result.errors:
        lines.append("Errors:")
        lines.extend(f"  - {msg}" for msg in result.errors)

    if result.ok and not uninstall and result.installed:
        lines.append("")
        lines.append(RELOAD_REMINDER)

    return "\n".join(lines)


def run_operation(
    *,
    target: Path,
    skills: Sequence[str],
    agents: Sequence[str],
    commands: Sequence[str],
    scripts: Sequence[str] = (),
    uninstall: bool = False,
    override: bool = False,
) -> tuple[int, str]:
    if not skills and not agents and not commands and not scripts:
        raise InstallerError("Select at least one skill, agent, command, or scripts.")

    if uninstall:
        result = uninstall_items(
            target_root=target,
            skills=skills,
            agents=agents,
            commands=commands,
            scripts=scripts,
        )
    else:
        result = install_items(
            source_root=REPO_ROOT,
            target_root=target,
            skills=skills,
            agents=agents,
            commands=commands,
            scripts=scripts,
            override=override,
        )

    message = format_result(result, uninstall=uninstall)
    if result.errors:
        return 1, message
    return 0, message


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Install or uninstall portable skills, agents, and commands from this AIConfig "
            "repository into another project."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python tools/installer.py /path/to/project\n"
            "  python tools/installer.py /path/to/project --skills cpp-coding\n"
            "  python tools/installer.py /path/to/project --commands git-commit\n"
            "  python tools/installer.py /path/to/project --bundles core-dev-workflow\n"
            "  python tools/installer.py /path/to/project --bundles extended-dev-workflow --override\n"
            "  python tools/installer.py /path/to/project --bundles core-dev-workflow --skills cpp-coding\n"
            "  python tools/installer.py /path/to/project --bundles target-bundle\n"
            "  python tools/installer.py /path/to/project --bundles dev-workflow-harness\n"
            "  python tools/installer.py /path/to/project --dev-workflow\n"
            "  python tools/installer.py /path/to/project --scripts dev-workflow\n"
            "  python tools/installer.py /path/to/project --uninstall --agents my-agent\n"
            "  python tools/installer.py /path/to/project --uninstall --commands git-commit\n"
            "\n"
            "Run without arguments to open the GUI."
        ),
    )
    parser.add_argument(
        "target",
        nargs="?",
        help="Destination project root.",
    )
    parser.add_argument(
        "--bundles",
        nargs="+",
        metavar="ID",
        help=(
            "Bundle ids from bundles.json or target-bundle to install or uninstall. "
            "A bundle may include skills, agents, commands, and scripts."
        ),
    )
    parser.add_argument(
        "--skills",
        nargs="+",
        metavar="NAME",
        help="Skill names to install or uninstall (default: all discovered skills unless --bundles is set).",
    )
    parser.add_argument(
        "--agents",
        nargs="+",
        metavar="NAME",
        help="Agent names to install or uninstall (default: all discovered agents).",
    )
    parser.add_argument(
        "--commands",
        nargs="+",
        metavar="NAME",
        help="Command names to install or uninstall (default: all discovered commands).",
    )
    parser.add_argument(
        "--scripts",
        nargs="+",
        metavar="NAME",
        help="Scripts directory names (under .ai/tools/) to install or uninstall (default: all discovered).",
    )
    parser.add_argument(
        "--dev-workflow",
        action="store_true",
        help=(
            "Alias for --bundles dev-workflow-harness: install or uninstall the complete "
            "dev-workflow harness (11 skills, 1 command, and the .ai/tools/dev-workflow/ scripts)."
        ),
    )
    parser.add_argument(
        "--uninstall",
        action="store_true",
        help="Remove the selected skills, agents, commands, and scripts from the target project.",
    )
    parser.add_argument(
        "--override",
        action="store_true",
        help="Replace existing skills, agents, commands, and scripts in the target project.",
    )
    return parser.parse_args(argv)


def run_cli(argv: Sequence[str]) -> int:
    args = parse_args(argv)
    if args.target is None:
        print("error: TARGET is required in CLI mode.", file=sys.stderr)
        print("Run without arguments to open the GUI.", file=sys.stderr)
        return 2

    try:
        target = Path(args.target).expanduser().resolve()
        # --dev-workflow is an alias for --bundles dev-workflow-harness.
        bundle_ids = list(args.bundles or [])
        if args.dev_workflow and "dev-workflow-harness" not in bundle_ids:
            bundle_ids.append("dev-workflow-harness")
        selection = resolve_cli_selection(
            bundle_ids=bundle_ids or None,
            skill_names=args.skills,
            agent_names=args.agents,
            command_names=args.commands,
            script_names=args.scripts,
            target_root=target,
        )
        code, message = run_operation(
            target=target,
            skills=selection.skills,
            agents=selection.agents,
            commands=selection.commands,
            scripts=selection.scripts,
            uninstall=args.uninstall,
            override=args.override,
        )
    except InstallerError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(message)
    return code


class HoverTooltip:
    """Show wrapped text in a delayed popup when the pointer hovers over a widget."""

    def __init__(self, widget: tk.Widget, text: str, *, delay_ms: int = 400) -> None:
        self.widget = widget
        self.text = text.strip()
        self.delay_ms = delay_ms
        self._tooltip: tk.Toplevel | None = None
        self._after_id: str | None = None

        if not self.text:
            return

        widget.bind("<Enter>", self._on_enter, add="+")
        widget.bind("<Leave>", self._on_leave, add="+")

    def _on_enter(self, _event: tk.Event) -> None:
        self._cancel_pending()
        self._after_id = self.widget.after(self.delay_ms, self._show)

    def _on_leave(self, _event: tk.Event) -> None:
        self._cancel_pending()
        self._hide()

    def _cancel_pending(self) -> None:
        if self._after_id is not None:
            self.widget.after_cancel(self._after_id)
            self._after_id = None

    def _show(self) -> None:
        self._after_id = None
        if self._tooltip is not None:
            return

        tooltip = tk.Toplevel(self.widget)
        tooltip.wm_overrideredirect(True)
        label = tk.Label(
            tooltip,
            text=self.text,
            justify=tk.LEFT,
            wraplength=420,
            relief=tk.SOLID,
            borderwidth=1,
            padx=8,
            pady=6,
        )
        label.pack()
        tooltip.update_idletasks()

        x = self.widget.winfo_pointerx() + 16
        y = self.widget.winfo_pointery() + 16
        tooltip.geometry(f"+{x}+{y}")
        self._tooltip = tooltip

    def _hide(self) -> None:
        if self._tooltip is not None:
            self._tooltip.destroy()
            self._tooltip = None

    def set_text(self, text: str) -> None:
        """Update tooltip text shown on the next hover."""
        self.text = text.strip()


class InstallerApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("AIConfig Installer")
        self.root.minsize(720, 520)

        self.skills = discover_skills()
        self.agents = discover_agents()
        self.commands = discover_commands()
        self.scripts = discover_scripts()
        self.skill_descriptions = load_skill_descriptions(self.skills)
        self.agent_descriptions = load_agent_descriptions(self.agents)
        self.command_descriptions = load_command_descriptions(self.commands)
        self.scripts_descriptions = load_scripts_descriptions(self.scripts)
        self.skill_vars: dict[str, tk.BooleanVar] = {}
        self.agent_vars: dict[str, tk.BooleanVar] = {}
        self.command_vars: dict[str, tk.BooleanVar] = {}
        self.scripts_vars: dict[str, tk.BooleanVar] = {}

        self.target_var = tk.StringVar()
        self.mode_var = tk.StringVar(value="install")
        self.override_var = tk.BooleanVar(value=False)
        self._syncing_bundle_selection = False
        self.skill_bundles = load_skill_bundles()
        self._bundle_buttons: dict[str, ttk.Checkbutton] = {}
        self._target_bundle: Bundle | None = None
        self._target_bundle_button: ttk.Checkbutton | None = None
        self._target_bundle_tooltip: HoverTooltip | None = None
        self._help_window: tk.Toplevel | None = None

        self._build_ui()
        self.target_var.trace_add("write", lambda *_args: self._refresh_target_bundle())
        self._refresh_target_bundle()

    def _build_ui(self) -> None:
        outer = ttk.Frame(self.root, padding=12)
        outer.pack(fill=tk.BOTH, expand=True)

        target_frame = ttk.LabelFrame(outer, text="Target project", padding=8)
        target_frame.pack(fill=tk.X, pady=(0, 8))
        ttk.Entry(target_frame, textvariable=self.target_var).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8)
        )
        ttk.Button(target_frame, text="Browse…", command=self._browse_target).pack(side=tk.LEFT)

        lists = ttk.Frame(outer)
        lists.pack(fill=tk.BOTH, expand=True)

        self._add_checkbox_list(
            lists,
            title="Skills",
            items=self.skills,
            var_map=self.skill_vars,
            column=0,
            skill_selection=True,
            descriptions=self.skill_descriptions,
            help_command=self._show_skills_help,
        )
        self._add_checkbox_list(
            lists,
            title="Agents",
            items=self.agents,
            var_map=self.agent_vars,
            column=1,
            descriptions=self.agent_descriptions,
            help_command=self._show_agents_help,
        )
        self._add_checkbox_list(
            lists,
            title="Commands",
            items=self.commands,
            var_map=self.command_vars,
            column=2,
            descriptions=self.command_descriptions,
            help_command=self._show_commands_help,
        )
        self._add_checkbox_list(
            lists,
            title="Scripts",
            items=self.scripts,
            var_map=self.scripts_vars,
            column=3,
            descriptions=self.scripts_descriptions,
            help_command=self._show_scripts_help,
        )

        self._add_bundles_panel(outer)

        options = ttk.LabelFrame(outer, text="Options", padding=8)
        options.pack(fill=tk.X, pady=8)
        ttk.Radiobutton(options, text="Install", variable=self.mode_var, value="install").pack(
            side=tk.LEFT, padx=(0, 12)
        )
        ttk.Radiobutton(
            options, text="Uninstall", variable=self.mode_var, value="uninstall"
        ).pack(side=tk.LEFT, padx=(0, 12))
        ttk.Checkbutton(options, text="Override existing", variable=self.override_var).pack(
            side=tk.LEFT
        )

        actions = ttk.Frame(outer)
        actions.pack(fill=tk.X, pady=(0, 8))
        ttk.Button(actions, text="Run", command=self._run).pack(side=tk.LEFT)
        ttk.Button(actions, text="Close", command=self.root.destroy).pack(side=tk.LEFT, padx=8)

        log_frame = ttk.LabelFrame(outer, text="Output", padding=8)
        log_frame.pack(fill=tk.BOTH, expand=True)
        self.log = scrolledtext.ScrolledText(log_frame, height=12, state=tk.DISABLED)
        self.log.pack(fill=tk.BOTH, expand=True)

    def _add_bundles_panel(self, parent: ttk.Frame) -> None:
        bundles = ttk.LabelFrame(parent, text="Bundles", padding=8)
        bundles.pack(fill=tk.X, pady=(0, 8))

        controls = ttk.Frame(bundles)
        controls.pack(fill=tk.X, pady=(0, 6))
        ttk.Button(
            controls,
            text="Select all",
            command=lambda: self._set_all_bundled_skills(True),
        ).pack(side=tk.LEFT)
        ttk.Button(
            controls,
            text="Select none",
            command=lambda: self._set_all_bundled_skills(False),
        ).pack(side=tk.LEFT, padx=6)
        ttk.Button(controls, text="Help", command=self._show_bundles_help).pack(side=tk.RIGHT)

        for bundle in self.skill_bundles:
            button = ttk.Checkbutton(
                bundles,
                text=bundle.name,
                command=lambda b=bundle: self._toggle_bundle(b),
            )
            button.pack(anchor=tk.W)
            self._bundle_buttons[bundle.id] = button
            if bundle.description.strip():
                HoverTooltip(button, bundle.description)

        target_button = ttk.Checkbutton(
            bundles,
            text=TARGET_BUNDLE_NAME,
            state=tk.DISABLED,
            command=self._toggle_target_bundle,
        )
        target_button.pack(anchor=tk.W)
        self._target_bundle_button = target_button
        self._bundle_buttons[TARGET_BUNDLE_ID] = target_button
        self._target_bundle_tooltip = HoverTooltip(
            target_button,
            "Set a target project to scan installed skills.",
        )

    def _add_checkbox_list(
        self,
        parent: ttk.Frame,
        *,
        title: str,
        items: list[str],
        var_map: dict[str, tk.BooleanVar],
        column: int,
        skill_selection: bool = False,
        descriptions: dict[str, str] | None = None,
        help_command: Callable[[], None] | None = None,
    ) -> None:
        frame = ttk.LabelFrame(parent, text=title, padding=8)
        if column == 0:
            padx = (0, 4)
        else:
            padx = (4, 4)
        frame.grid(row=0, column=column, sticky="nsew", padx=padx)
        parent.columnconfigure(column, weight=1)
        parent.rowconfigure(0, weight=1)

        controls = ttk.Frame(frame)
        controls.pack(fill=tk.X, pady=(0, 6))
        if skill_selection:
            ttk.Button(
                controls,
                text="Select all",
                command=lambda: self._set_all_skills(True),
            ).pack(side=tk.LEFT)
            ttk.Button(
                controls,
                text="Select none",
                command=lambda: self._set_all_skills(False),
            ).pack(side=tk.LEFT, padx=6)
        else:
            ttk.Button(
                controls,
                text="Select all",
                command=lambda: self._set_all(var_map, True),
            ).pack(side=tk.LEFT)
            ttk.Button(
                controls,
                text="Select none",
                command=lambda: self._set_all(var_map, False),
            ).pack(side=tk.LEFT, padx=6)
        if help_command is not None:
            ttk.Button(controls, text="Help", command=help_command).pack(side=tk.RIGHT)

        canvas = tk.Canvas(frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
        inner = ttk.Frame(canvas)
        inner.bind(
            "<Configure>",
            lambda _event: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        for item in items:
            var = tk.BooleanVar(value=False)
            var_map[item] = var
            var.trace_add("write", lambda *_args: self._on_selection_changed())
            button = ttk.Checkbutton(inner, text=item, variable=var)
            button.pack(anchor=tk.W)
            if descriptions is not None:
                description = descriptions.get(item)
                if description:
                    HoverTooltip(button, description)

        if not items:
            ttk.Label(inner, text="(none discovered)").pack(anchor=tk.W)

    def _set_all(self, var_map: dict[str, tk.BooleanVar], value: bool) -> None:
        for var in var_map.values():
            var.set(value)

    def _set_all_skills(self, value: bool) -> None:
        self._syncing_bundle_selection = True
        try:
            self._set_all(self.skill_vars, value)
        finally:
            self._syncing_bundle_selection = False
        self._sync_bundle_toggles()

    def _effective_bundles(self) -> list[Bundle]:
        bundles = list(self.skill_bundles)
        if self._target_bundle is not None:
            bundles.append(self._target_bundle)
        return bundles

    def _bundle_member_pairs(self, bundle: Bundle) -> list[tuple[frozenset[str], dict[str, tk.BooleanVar]]]:
        """Return (members, var_map) pairs for each kind present in the bundle."""
        pairs: list[tuple[frozenset[str], dict[str, tk.BooleanVar]]] = []
        if bundle.skills:
            pairs.append((bundle.skills, self.skill_vars))
        if bundle.agents:
            pairs.append((bundle.agents, self.agent_vars))
        if bundle.commands:
            pairs.append((bundle.commands, self.command_vars))
        if bundle.scripts:
            pairs.append((bundle.scripts, self.scripts_vars))
        return pairs

    def _bundle_present_members(self, members: frozenset[str], var_map: dict[str, tk.BooleanVar]) -> list[str]:
        return sorted(name for name in members if name in var_map)

    def _all_bundled_member_names(self) -> list[str]:
        names: set[str] = set()
        for bundle in self._effective_bundles():
            for members, var_map in self._bundle_member_pairs(bundle):
                names.update(self._bundle_present_members(members, var_map))
        return sorted(names)

    def _set_all_bundled_skills(self, value: bool) -> None:
        present = self._all_bundled_member_names()
        if not present:
            return
        self._syncing_bundle_selection = True
        try:
            for bundle in self._effective_bundles():
                for members, var_map in self._bundle_member_pairs(bundle):
                    for name in self._bundle_present_members(members, var_map):
                        var_map[name].set(value)
        finally:
            self._syncing_bundle_selection = False
        self._sync_bundle_toggles()

    def _toggle_bundle(self, bundle: Bundle) -> None:
        # Collect all present members across all kinds to determine the toggle state.
        all_present: list[str] = []
        member_var_pairs: list[tuple[list[str], dict[str, tk.BooleanVar]]] = []
        for members, var_map in self._bundle_member_pairs(bundle):
            present = self._bundle_present_members(members, var_map)
            all_present.extend(present)
            member_var_pairs.append((present, var_map))
        if not all_present:
            return
        state = bundle_selection_state(all_present, lambda name: self._member_is_selected(name, bundle))
        new_value = bundle_toggle_target_state(state)
        self._syncing_bundle_selection = True
        try:
            for present, var_map in member_var_pairs:
                for name in present:
                    var_map[name].set(new_value)
        finally:
            self._syncing_bundle_selection = False
        self._sync_bundle_toggles()

    def _member_is_selected(self, name: str, bundle: Bundle) -> bool:
        """Return True if a bundle member is currently checked in its var_map."""
        for members, var_map in self._bundle_member_pairs(bundle):
            if name in var_map:
                return var_map[name].get()
        return False

    def _toggle_target_bundle(self) -> None:
        if self._target_bundle is None:
            return
        self._toggle_bundle(self._target_bundle)

    def _update_target_bundle_tooltip(self, text: str) -> None:
        if self._target_bundle_tooltip is not None:
            self._target_bundle_tooltip.set_text(text)

    def _refresh_target_bundle(self) -> None:
        button = self._target_bundle_button
        if button is None:
            return

        self._target_bundle = None
        target_text = self.target_var.get().strip()
        if not target_text:
            button.state(["disabled"])
            self._update_target_bundle_tooltip("Set a target project to scan installed members.")
            self._sync_bundle_toggles()
            return

        try:
            target = Path(target_text).expanduser().resolve()
        except (OSError, RuntimeError):
            button.state(["disabled"])
            self._update_target_bundle_tooltip("Invalid target path.")
            self._sync_bundle_toggles()
            return

        if not target.exists() or not target.is_dir():
            button.state(["disabled"])
            self._update_target_bundle_tooltip("Target must be an existing directory.")
            self._sync_bundle_toggles()
            return

        try:
            validate_target(REPO_ROOT, target, create=False)
        except InstallerError as exc:
            button.state(["disabled"])
            self._update_target_bundle_tooltip(str(exc))
            self._sync_bundle_toggles()
            return

        bundle = build_target_bundle(
            target,
            available_skills=self.skills,
            available_agents=self.agents,
            available_commands=self.commands,
            available_scripts=self.scripts,
        )
        if bundle.is_empty:
            button.state(["disabled"])
            self._update_target_bundle_tooltip(
                f"{TARGET_BUNDLE_DESCRIPTION} No matching installed members found in target."
            )
            self._sync_bundle_toggles()
            return

        self._target_bundle = bundle
        button.state(["!disabled"])
        counts = [
            (len(bundle.skills), "skill"),
            (len(bundle.agents), "agent"),
            (len(bundle.commands), "command"),
            (len(bundle.scripts), "script"),
        ]
        parts = [f"{count} {word}{'s' if count != 1 else ''}" for count, word in counts if count]
        self._update_target_bundle_tooltip(
            f"{TARGET_BUNDLE_DESCRIPTION} {', '.join(parts)} installed in target."
        )
        self._sync_bundle_toggles()

    def _on_selection_changed(self) -> None:
        if self._syncing_bundle_selection:
            return
        self._sync_bundle_toggles()

    def _apply_bundle_toggle_state(
        self,
        widget: ttk.Checkbutton,
        state: BundleSelectionState,
    ) -> None:
        if state == "all":
            widget.state(["!alternate", "selected"])
        elif state == "none":
            widget.state(["!alternate", "!selected"])
        else:
            widget.state(["alternate", "!selected"])

    def _sync_bundle_toggles(self) -> None:
        if not self._bundle_buttons:
            return

        for bundle in self._effective_bundles():
            button = self._bundle_buttons.get(bundle.id)
            if button is None:
                continue
            all_present: list[str] = []
            for members, var_map in self._bundle_member_pairs(bundle):
                all_present.extend(self._bundle_present_members(members, var_map))
            state = bundle_selection_state(
                all_present,
                lambda name: self._member_is_selected(name, bundle),
            )
            self._apply_bundle_toggle_state(button, state)

        target_button = self._bundle_buttons.get(TARGET_BUNDLE_ID)
        if target_button is not None and self._target_bundle is None:
            self._apply_bundle_toggle_state(target_button, "none")

    def _browse_target(self) -> None:
        selected = filedialog.askdirectory(title="Select target project root")
        if selected:
            self.target_var.set(selected)

    def _append_log(self, text: str) -> None:
        self.log.configure(state=tk.NORMAL)
        self.log.insert(tk.END, text + "\n")
        self.log.see(tk.END)
        self.log.configure(state=tk.DISABLED)

    def _selected(self, var_map: dict[str, tk.BooleanVar]) -> list[str]:
        return sorted(name for name, var in var_map.items() if var.get())

    def _help_entries_for_selection(
        self,
        names: Sequence[str],
        descriptions: dict[str, str],
    ) -> list[tuple[str, str]]:
        return [(name, descriptions.get(name, "")) for name in names]

    def _show_help_window(self, title: str, content: str) -> None:
        if self._help_window is not None:
            try:
                if self._help_window.winfo_exists():
                    self._help_window.destroy()
            except tk.TclError:
                pass
            self._help_window = None

        window = tk.Toplevel(self.root)
        window.title(title)
        window.minsize(520, 360)
        window.transient(self.root)
        self._help_window = window

        frame = ttk.Frame(window, padding=12)
        frame.pack(fill=tk.BOTH, expand=True)

        text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, width=72, height=18)
        text.pack(fill=tk.BOTH, expand=True)
        text.insert(tk.END, content)
        text.bind("<Key>", lambda _event: "break")

        actions = ttk.Frame(frame)
        actions.pack(fill=tk.X, pady=(8, 0))
        ttk.Button(actions, text="Close", command=window.destroy).pack(side=tk.RIGHT)

        window.lift()
        window.focus_force()

    def _show_skills_help(self) -> None:
        names = self._selected(self.skill_vars)
        entries = self._help_entries_for_selection(names, self.skill_descriptions)
        content = format_selection_help(entries, empty_message="No skills selected.")
        self._show_help_window("Skills — Help", content)

    def _show_agents_help(self) -> None:
        names = self._selected(self.agent_vars)
        entries = self._help_entries_for_selection(names, self.agent_descriptions)
        content = format_selection_help(entries, empty_message="No agents selected.")
        self._show_help_window("Agents — Help", content)

    def _show_commands_help(self) -> None:
        names = self._selected(self.command_vars)
        entries = self._help_entries_for_selection(names, self.command_descriptions)
        content = format_selection_help(entries, empty_message="No commands selected.")
        self._show_help_window("Commands — Help", content)

    def _show_scripts_help(self) -> None:
        names = self._selected(self.scripts_vars)
        entries = self._help_entries_for_selection(names, self.scripts_descriptions)
        content = format_selection_help(entries, empty_message="No scripts selected.")
        self._show_help_window("Scripts — Help", content)

    def _show_bundles_help(self) -> None:
        def present(bundle: Bundle) -> Sequence[str]:
            names: list[str] = []
            for members, var_map in self._bundle_member_pairs(bundle):
                names.extend(self._bundle_present_members(members, var_map))
            return names

        entries = bundle_help_entries(
            self._effective_bundles(),
            present_members=present,
            is_selected=lambda name: self._member_is_selected_any(name),
        )
        content = format_selection_help(entries, empty_message="No bundles selected.")
        self._show_help_window("Bundles — Help", content)

    def _member_is_selected_any(self, name: str) -> bool:
        """Return True if name is checked in any var_map."""
        for var_map in (self.skill_vars, self.agent_vars, self.command_vars, self.scripts_vars):
            var = var_map.get(name)
            if var is not None and var.get():
                return True
        return False

    def _run(self) -> None:
        target_text = self.target_var.get().strip()
        if not target_text:
            messagebox.showerror("Missing target", "Choose a target project folder.")
            return

        skills = self._selected(self.skill_vars)
        agents = self._selected(self.agent_vars)
        commands = self._selected(self.command_vars)
        scripts = self._selected(self.scripts_vars)
        if not skills and not agents and not commands and not scripts:
            messagebox.showerror(
                "Nothing selected",
                "Select at least one skill, agent, command, or scripts.",
            )
            return

        try:
            target = Path(target_text).expanduser().resolve()
            code, message = run_operation(
                target=target,
                skills=skills,
                agents=agents,
                commands=commands,
                scripts=scripts,
                uninstall=self.mode_var.get() == "uninstall",
                override=self.override_var.get(),
            )
        except InstallerError as exc:
            messagebox.showerror("Error", str(exc))
            return

        self._append_log(message)
        if code != 0:
            messagebox.showwarning("Completed with errors", "See output for details.")


def run_gui() -> int:
    if not sys.platform.startswith("win") and not os.environ.get("DISPLAY"):
        print(
            "error: No display available for the GUI.\n"
            "Use the CLI instead, for example:\n"
            "  python tools/installer.py /path/to/project",
            file=sys.stderr,
        )
        return 2

    try:
        root = tk.Tk()
    except tk.TclError as exc:
        print(f"error: Could not start GUI: {exc}", file=sys.stderr)
        print(
            "Use the CLI instead, for example:\n"
            "  python tools/installer.py /path/to/project",
            file=sys.stderr,
        )
        return 2

    try:
        InstallerApp(root)
    except InstallerError as exc:
        root.destroy()
        messagebox.showerror("Bundle config error", str(exc))
        return 2

    root.mainloop()
    return 0


def main() -> int:
    if len(sys.argv) == 1:
        return run_gui()
    return run_cli(sys.argv[1:])


if __name__ == "__main__":
    raise SystemExit(main())
