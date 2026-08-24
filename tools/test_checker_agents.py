#!/usr/bin/env python3
"""Structural tests for the four dev-workflow checker agents.

Validates that each checker agent:
- Has a bootstrap AGENT.md and three tool wrappers (FR-1)
- Points to its corresponding skill (FR-2)
- Has per-host read-only enforcement (FR-3)
- Has model pinning per wrapper (FR-4)
- Has a differentiated description from the skill (FR-12, rr-008)

Also validates orchestrator edits:
- dispatch-modes.md reference exists (FR-5)
- orchestrator SKILL.md references dispatch-modes.md (FR-6)
- task packet construction documented (FR-7)
- manifest-format.md has Dispatch log section (FR-9)
- prior-round -r1 copy documented (FR-11)
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

WRAPPER_REL_PATHS = {
    "cursor": "wrappers/cursor/AGENT.md",
    "claude": "wrappers/claude/AGENT.md",
    "github": "wrappers/github/AGENT.md",
}

INSTALLED_WRAPPER_PATHS = {
    "cursor": ".cursor/agents/{name}.md",
    "claude": ".claude/agents/{name}.md",
    "github": ".github/agents/{name}.agent.md",
}


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

    def test_all_four_have_three_wrappers(self):
        """t-002: Each checker has wrappers/{cursor,claude,github}/AGENT.md."""
        for name in CHECKER_AGENTS:
            for tool, rel in WRAPPER_REL_PATHS.items():
                wrapper = REPO_ROOT / "agents" / name / rel
                self.assertTrue(
                    wrapper.is_file(),
                    f"Missing {tool} wrapper for {name}: {wrapper}",
                )


class CheckerAgentContentTests(unittest.TestCase):
    """t-003, t-004, t-010, t-012: Agent content checks."""

    def test_agent_points_to_skill(self):
        """t-003: Each AGENT.md references .ai/skills/<name>/SKILL.md."""
        for name in CHECKER_AGENTS:
            agent_md = REPO_ROOT / "agents" / name / "AGENT.md"
            content = agent_md.read_text(encoding="utf-8")
            expected_ref = f".ai/skills/{name}/SKILL.md"
            self.assertIn(
                expected_ref,
                content,
                f"{agent_md} does not reference skill at {expected_ref}",
            )

    def test_readonly_enforcement_per_host(self):
        """t-004: Cursor has readonly:true in frontmatter, Claude has tools restriction in frontmatter, Copilot documents instruction-only."""
        for name in CHECKER_AGENTS:
            # Cursor: readonly: true in frontmatter
            cursor_wrapper = REPO_ROOT / "agents" / name / "wrappers" / "cursor" / "AGENT.md"
            cursor_fm = parse_frontmatter(cursor_wrapper.read_text(encoding="utf-8"))
            self.assertIn(
                "readonly",
                cursor_fm,
                f"Cursor wrapper for {name} missing 'readonly' frontmatter field",
            )
            self.assertTrue(
                cursor_fm["readonly"] is True or cursor_fm["readonly"] == "true",
                f"Cursor wrapper for {name} 'readonly' field is not true: {cursor_fm.get('readonly')}",
            )
            # Claude: tools: restricted in frontmatter (not Edit/Write)
            claude_wrapper = REPO_ROOT / "agents" / name / "wrappers" / "claude" / "AGENT.md"
            claude_fm = parse_frontmatter(claude_wrapper.read_text(encoding="utf-8"))
            self.assertIn(
                "tools",
                claude_fm,
                f"Claude wrapper for {name} missing 'tools' frontmatter field",
            )
            # Copilot: documents instruction-only enforcement
            github_wrapper = REPO_ROOT / "agents" / name / "wrappers" / "github" / "AGENT.md"
            github_content = github_wrapper.read_text(encoding="utf-8")
            self.assertIn(
                "instruction-only",
                github_content.lower(),
                f"GitHub wrapper for {name} missing instruction-only documentation",
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

    def test_model_pinning_per_wrapper(self):
        """t-012: Each wrapper has a non-empty model: field in frontmatter (structural proxy for model pinning)."""
        for name in CHECKER_AGENTS:
            for tool, rel in WRAPPER_REL_PATHS.items():
                wrapper = REPO_ROOT / "agents" / name / rel
                content = wrapper.read_text(encoding="utf-8")
                frontmatter = parse_frontmatter(content)
                self.assertIn(
                    "model",
                    frontmatter,
                    f"{tool} wrapper for {name} missing 'model:' frontmatter field",
                )
                self.assertTrue(
                    frontmatter["model"],
                    f"{tool} wrapper for {name} has empty 'model:' field",
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
    """Verify installed agent paths exist and are valid."""

    def test_all_installed_shared_agents_exist(self):
        """Each checker has .ai/agents/<name>.md installed."""
        for name in CHECKER_AGENTS:
            path = REPO_ROOT / ".ai" / "agents" / f"{name}.md"
            self.assertTrue(path.is_file(), f"Missing installed shared agent: {path}")

    def test_all_installed_tool_wrappers_exist(self):
        """Each checker has tool wrappers installed in .cursor/, .claude/, .github/."""
        for name in CHECKER_AGENTS:
            for tool, rel_template in INSTALLED_WRAPPER_PATHS.items():
                path = REPO_ROOT / rel_template.format(name=name)
                self.assertTrue(
                    path.is_file(),
                    f"Missing installed {tool} wrapper for {name}: {path}",
                )


if __name__ == "__main__":
    unittest.main()
