#!/usr/bin/env python3
"""Structural tests for the four dev-workflow checker agents.

Validates that each checker agent:
- Has a bootstrap AGENT.md with a `## Tool notes` section (FR-1, post-merge)
- Points to its corresponding skill (FR-2)
- Documents per-host read-only enforcement in Tool notes (FR-3)
- Documents model inheritance per host in Tool notes (FR-4)
- Has a differentiated description from the skill (FR-12, rr-008)

Also validates orchestrator edits:
- dispatch-modes.md reference exists (FR-5)
- orchestrator SKILL.md references dispatch-modes.md (FR-6)
- task packet construction documented (FR-7)
- manifest-format.md has Dispatch log section (FR-9)
- prior-round -r1 copy documented (FR-11)

Bootstrap-side (post Tool-notes merge). Installed-path tests live in
InstalledPathTests and assert the post-migration dual-target layout.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent

CHECKER_AGENTS = (
    "research-reviewer",
    "plan-reviewer",
    "implementation-auditor",
    "code-reviewer",
)

def parse_frontmatter(content: str) -> dict:
    """Parse YAML frontmatter from a markdown file.

    Uses yaml.safe_load for robust parsing of quoted strings, multi-line values,
    and nested structures. Falls back to empty dict on parse errors.
    """
    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return {}
    try:
        result = yaml.safe_load(match.group(1))
        return result if isinstance(result, dict) else {}
    except yaml.YAMLError:
        return {}


class CheckerAgentBootstrapTests(unittest.TestCase):
    """t-001, t-002: All four bootstrap agent dirs and wrappers exist."""

    def test_all_four_bootstrap_dirs_exist(self):
        """t-001: Each checker has an agents/<name>/AGENT.md."""
        for name in CHECKER_AGENTS:
            agent_md = REPO_ROOT / "agents" / name / "AGENT.md"
            self.assertTrue(agent_md.is_file(), f"Missing bootstrap AGENT.md: {agent_md}")

    def test_all_four_have_tool_notes_section(self):
        """t-002 (post-merge): Each AGENT.md has a `## Tool notes` section."""
        for name in CHECKER_AGENTS:
            agent_md = REPO_ROOT / "agents" / name / "AGENT.md"
            content = agent_md.read_text(encoding="utf-8")
            self.assertRegex(
                content,
                r"(?m)^## Tool notes\s*$",
                f"{agent_md} missing '## Tool notes' section",
            )


class CheckerAgentContentTests(unittest.TestCase):
    """t-003, t-004, t-010, t-012: Agent content checks."""

    def test_agent_points_to_skill(self):
        """t-003: Each AGENT.md references .agents/skills/<name>/SKILL.md."""
        for name in CHECKER_AGENTS:
            agent_md = REPO_ROOT / "agents" / name / "AGENT.md"
            content = agent_md.read_text(encoding="utf-8")
            expected_ref = f".agents/skills/{name}/SKILL.md"
            self.assertIn(
                expected_ref,
                content,
                f"{agent_md} does not reference skill at {expected_ref}",
            )

    def test_readonly_enforcement_documented_per_host(self):
        """t-004 (cr-205/ia-002): Tool notes document the verbatim-copy reality —
        Claude and Cursor hosts carry no readonly/tools frontmatter keys (the
        installer copies AGENT.md verbatim), Copilot is instruction-only."""
        for name in CHECKER_AGENTS:
            agent_md = REPO_ROOT / "agents" / name / "AGENT.md"
            content = agent_md.read_text(encoding="utf-8")
            tool_notes = content.split("## Tool notes", 1)
            self.assertEqual(
                len(tool_notes),
                2,
                f"{agent_md} missing '## Tool notes' section for host checks",
            )
            notes = tool_notes[1]
            self.assertIn(
                "verbatim copy of this AGENT.md",
                notes,
                f"{agent_md} Tool notes missing verbatim-copy (no host frontmatter keys) documentation",
            )
            self.assertIn(
                "no `tools:` or `model:` keys",
                notes,
                f"{agent_md} Tool notes missing Claude no-host-frontmatter-keys documentation",
            )
            self.assertIn(
                "no `readonly:` key",
                notes,
                f"{agent_md} Tool notes missing Cursor no-readonly-key documentation",
            )
            self.assertIn(
                "instruction-only",
                notes.lower(),
                f"{agent_md} Tool notes missing Copilot instruction-only documentation",
            )

    def test_agent_description_differs_from_skill(self):
        """t-010: Agent description contains 'isolated' or 'fresh-context' (structural proxy for differentiation)."""
        for name in CHECKER_AGENTS:
            agent_md = REPO_ROOT / "agents" / name / "AGENT.md"
            content = agent_md.read_text(encoding="utf-8")
            frontmatter = parse_frontmatter(content)
            description = frontmatter.get("description", "")
            self.assertTrue(
                "isolated" in description.lower() or "fresh-context" in description.lower(),
                f"Agent {name} description lacks 'isolated' or 'fresh-context' — "
                f"may not be differentiated from the skill description",
            )

    def test_model_inheritance_documented_per_host(self):
        """t-012 (cr-205/ia-002): Tool notes document the default-model reality —
        installed copies carry no `model:` key, so Claude/Cursor run on the
        conversation/parent model and Copilot on the user's selected chat model."""
        for name in CHECKER_AGENTS:
            agent_md = REPO_ROOT / "agents" / name / "AGENT.md"
            content = agent_md.read_text(encoding="utf-8")
            tool_notes = content.split("## Tool notes", 1)
            self.assertEqual(
                len(tool_notes),
                2,
                f"{agent_md} missing '## Tool notes' section for model checks",
            )
            notes = tool_notes[1]
            self.assertIn(
                "With no `model:` key",
                notes,
                f"{agent_md} Tool notes missing no-model-key default-model documentation",
            )
            self.assertIn(
                "user's currently selected Copilot chat model",
                notes,
                f"{agent_md} Tool notes missing Copilot selected-model documentation",
            )


class OrchestratorEditTests(unittest.TestCase):
    """t-005 through t-009: Orchestrator reference and procedure edits."""

    def test_dispatch_modes_reference_exists(self):
        """t-005: references/dispatch-modes.md exists."""
        path = REPO_ROOT / "skills" / "dev-workflow-orchestrator" / "references" / "dispatch-modes.md"
        self.assertTrue(path.is_file(), f"Missing dispatch-modes.md: {path}")

    def test_orchestrator_dispatch_model_references_modes(self):
        """t-006: orchestrator SKILL.md references dispatch-modes.md."""
        skill_md = REPO_ROOT / "skills" / "dev-workflow-orchestrator" / "SKILL.md"
        content = skill_md.read_text(encoding="utf-8")
        self.assertIn(
            "dispatch-modes.md",
            content,
            "Orchestrator SKILL.md does not reference dispatch-modes.md",
        )

    def test_task_packet_construction_documented(self):
        """t-007: orchestrator procedure mentions task packet construction."""
        skill_md = REPO_ROOT / "skills" / "dev-workflow-orchestrator" / "SKILL.md"
        content = skill_md.read_text(encoding="utf-8")
        self.assertIn(
            "task packet",
            content.lower(),
            "Orchestrator SKILL.md does not mention task packet construction",
        )

    def test_manifest_format_has_dispatch_log(self):
        """t-008: manifest-format.md has ## Dispatch log section."""
        manifest_fmt = REPO_ROOT / "skills" / "dev-workflow-orchestrator" / "references" / "manifest-format.md"
        content = manifest_fmt.read_text(encoding="utf-8")
        self.assertIn(
            "## Dispatch log",
            content,
            "manifest-format.md missing '## Dispatch log' section",
        )

    def test_prior_round_r1_copy_documented(self):
        """t-009: orchestrator procedure documents the -r1 copy step."""
        skill_md = REPO_ROOT / "skills" / "dev-workflow-orchestrator" / "SKILL.md"
        content = skill_md.read_text(encoding="utf-8")
        self.assertIn(
            "-r1",
            content,
            "Orchestrator SKILL.md does not document the prior-round -r1 copy step",
        )


class InstalledPathTests(unittest.TestCase):
    """Verify installed agent paths exist and are valid (post-migration layout).

    The single-root migration removed the old installed shared-agent tree and
    the Cursor agent wrappers: agents are now dual-target
    (Claude Code + GitHub Copilot) as verbatim AGENT.md copies at
    `.claude/agents/<name>.md` and `.github/agents/<name>.agent.md`.
    """

    def test_all_installed_claude_agent_copies_exist(self):
        """Each checker has a .claude/agents/<name>.md installed copy."""
        for name in CHECKER_AGENTS:
            path = REPO_ROOT / ".claude" / "agents" / f"{name}.md"
            self.assertTrue(path.is_file(), f"Missing installed Claude agent: {path}")

    def test_all_installed_github_agent_copies_exist(self):
        """Each checker has a .github/agents/<name>.agent.md installed copy."""
        for name in CHECKER_AGENTS:
            path = REPO_ROOT / ".github" / "agents" / f"{name}.agent.md"
            self.assertTrue(path.is_file(), f"Missing installed GitHub agent: {path}")

    def test_installed_copies_are_verbatim_of_bootstrap(self):
        """Installed .claude/agents/<name>.md matches bootstrap AGENT.md verbatim."""
        for name in CHECKER_AGENTS:
            bootstrap = (REPO_ROOT / "agents" / name / "AGENT.md").read_text(encoding="utf-8")
            installed = (REPO_ROOT / ".claude" / "agents" / f"{name}.md").read_text(encoding="utf-8")
            self.assertEqual(
                installed,
                bootstrap,
                f"Installed .claude/agents/{name}.md is not a verbatim copy of the bootstrap AGENT.md",
            )


if __name__ == "__main__":
    unittest.main()
