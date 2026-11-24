#!/usr/bin/env python3
"""Structural tests for the four dev-workflow checker agents.

Validates that each checker agent:
- Has a bootstrap AGENT.md with NO `## Tool notes` section — per-host install reality
  lives once in agent-creator's portable-agent-layout.md (post-migration contract)
- Points to its corresponding skill
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

    def test_all_four_have_no_tool_notes(self):
        """t-002 (post-merge): Each AGENT.md has no `## Tool notes` section —
        per-host install reality is documented once in agent-creator's
        portable-agent-layout.md, not duplicated (or pointed at) in every
        agent body that becomes the subagent prompt on native dispatch."""
        for name in CHECKER_AGENTS:
            agent_md = REPO_ROOT / "agents" / name / "AGENT.md"
            content = agent_md.read_text(encoding="utf-8")
            self.assertNotRegex(
                content,
                r"(?m)^## Tool notes\s*$",
                f"{agent_md} has a '## Tool notes' section — remove it; the shared "
                f"per-host reality lives in agent-creator's portable-agent-layout.md",
            )
            self.assertNotIn(
                "portable-agent-layout.md",
                content,
                f"{agent_md} references agent-creator's portable-agent-layout.md, "
                f"which is absent from distribution targets (installer ships only "
                f"the dual-target agent files)",
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

    SHARED_TOOL_NOTES_REF = (
        REPO_ROOT / "skills" / "agent-creator" / "references" / "portable-agent-layout.md"
    )
    SHARED_SECTION_HEADING = "Read-only checker agents: per-host reality"

    def test_readonly_enforcement_documented_per_host(self):
        """t-004 (cr-205/ia-002): The shared per-host reality section in
        agent-creator's portable-agent-layout.md documents the verbatim-copy
        reality — the Claude Code host carries no `tools:` or `model:`
        frontmatter keys (the installer copies AGENT.md verbatim), Copilot is
        instruction-only. The AGENT.md bodies carry no Tool notes sections."""
        shared = self.SHARED_TOOL_NOTES_REF.read_text(encoding="utf-8")
        self.assertIn(
            self.SHARED_SECTION_HEADING,
            shared,
            "portable-agent-layout.md missing shared per-host Tool notes section",
        )
        self.assertIn("no `tools:` or `model:` keys", shared,
                      "shared Tool notes missing Claude no-host-frontmatter-keys documentation")
        self.assertIn("instruction-only", shared.lower(),
                      "shared Tool notes missing Copilot instruction-only documentation")
        for name in CHECKER_AGENTS:
            agent_md = REPO_ROOT / "agents" / name / "AGENT.md"
            content = agent_md.read_text(encoding="utf-8")
            self.assertNotIn("## Tool notes", content,
                              f"{agent_md} has a '## Tool notes' section for host checks")

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
        """t-012 (cr-205/ia-002): The shared per-host reality section documents
        the default-model reality — installed copies carry no `model:` key, so
        Claude Code runs on the conversation model and Copilot on the
        user's selected chat model. The AGENT.md bodies carry no Tool notes."""
        shared = self.SHARED_TOOL_NOTES_REF.read_text(encoding="utf-8")
        self.assertIn(
            "with no `model:` key",
            shared.lower(),
            "shared Tool notes missing no-model-key default-model documentation",
        )
        self.assertIn(
            "user's currently selected Copilot chat model",
            shared,
            "shared Tool notes missing Copilot selected-model documentation",
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

    # Installed agent files (.claude/agents/, .github/agents/) are generated
    # by install_portable_agent.py and untracked in this repo — these guards
    # apply only when the checkout carries a local install (skip-when-absent
    # so a fresh clone passes before anything is installed).

    def test_all_installed_claude_agent_copies_exist(self):
        """Each checker has a .claude/agents/<name>.md installed copy."""
        for name in CHECKER_AGENTS:
            path = REPO_ROOT / ".claude" / "agents" / f"{name}.md"
            if not (REPO_ROOT / ".claude" / "agents").is_dir():
                self.skipTest("no local agent install in this checkout")
            self.assertTrue(path.is_file(), f"Missing installed Claude agent: {path}")

    def test_all_installed_github_agent_copies_exist(self):
        """Each checker has a .github/agents/<name>.agent.md installed copy."""
        for name in CHECKER_AGENTS:
            path = REPO_ROOT / ".github" / "agents" / f"{name}.agent.md"
            if not (REPO_ROOT / ".github" / "agents").is_dir():
                self.skipTest("no local agent install in this checkout")
            self.assertTrue(path.is_file(), f"Missing installed GitHub agent: {path}")

    def test_installed_copies_are_verbatim_of_bootstrap(self):
        """Installed .claude/agents/<name>.md matches bootstrap AGENT.md verbatim."""
        for name in CHECKER_AGENTS:
            bootstrap = (REPO_ROOT / "agents" / name / "AGENT.md").read_text(encoding="utf-8")
            installed_path = REPO_ROOT / ".claude" / "agents" / f"{name}.md"
            if not installed_path.is_file():
                self.skipTest("no local agent install in this checkout")
            installed = installed_path.read_text(encoding="utf-8")
            self.assertEqual(
                installed,
                bootstrap,
                f"Installed .claude/agents/{name}.md is not a verbatim copy of the bootstrap AGENT.md",
            )


if __name__ == "__main__":
    unittest.main()
