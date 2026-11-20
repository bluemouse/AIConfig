#!/usr/bin/env python3
"""Tests for the ar-012 unpaired-agent-skill warning (review round fixes cr-003, cr-004).

cr-003: OperationResult.warnings was collected but never surfaced —
format_result printed only installed/skipped/removed/errors, so the
"also pass --skills <slug>" advice never reached the user. format_result now
prints a Warnings: section.

cr-004: the 19-line warning block was pasted into the skills, commands, and
guidelines loops, where it is dead (the skills loop can never fire it; the
commands and guidelines loops inspect unrelated destinations). The logic now
lives in warn_unpaired_agent_skill(), called only from the agents loop.

Run from the repository root: python tools/test_installer_agent_skill_warning.py
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

import installer  # type: ignore[import-not-found]


def write_source_skill(root: Path, name: str) -> None:
    shared = root / ".agents" / "skills" / name / "SKILL.md"
    shared.parent.mkdir(parents=True, exist_ok=True)
    shared.write_text(
        f"---\nname: {name}\ndescription: {name} skill\n---\n\n# {name}\n",
        encoding="utf-8",
    )


def write_source_agent(root: Path, name: str, references_skill: bool) -> None:
    """Write a minimal dual-target agent; optionally one whose body
    references its paired skill (the checker-agent shape)."""
    body_ref = (
        "Load and follow the skill criteria at "
        f"`.agents/skills/{name}/SKILL.md`.\n"
        if references_skill
        else ""
    )
    for rel in (
        Path(".claude") / "agents" / f"{name}.md",
        Path(".github") / "agents" / f"{name}.agent.md",
    ):
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            f"---\nname: {name}\ndescription: {name} agent\n---\n\n# {name}\n\n{body_ref}",
            encoding="utf-8",
        )


class UnpairedAgentSkillWarningTests(unittest.TestCase):
    def _install(self, source: Path, target: Path, **kwargs) -> installer.OperationResult:
        return installer.install_items(
            source_root=source,
            target_root=target,
            skills=kwargs.pop("skills", []),
            agents=kwargs.pop("agents", []),
            commands=kwargs.pop("commands", []),
            override=True,
        )

    def test_agent_without_paired_skill_warns_and_surfaces(self) -> None:
        """cr-003: a checker-shaped agent installed without its skill
        produces a warning that reaches the formatted output."""
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            target = Path(tmp) / "target"
            source.mkdir()
            target.mkdir()
            write_source_agent(source, "code-reviewer", references_skill=True)

            result = self._install(source, target, agents=["code-reviewer"])
            self.assertTrue(result.ok)
            self.assertEqual(
                len(result.warnings),
                1,
                f"expected one unpaired-skill warning: {result.warnings}",
            )
            self.assertIn("--skills code-reviewer", result.warnings[0])
            message = installer.format_result(result, uninstall=False)
            self.assertIn("Warnings:", message, f"warning must surface: {message}")
            self.assertIn("--skills code-reviewer", message)

    def test_agent_with_paired_skill_no_warning(self) -> None:
        """Skill installed in the same pass: the reference resolves, no
        warning (also proves the helper's install-set check)."""
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            target = Path(tmp) / "target"
            source.mkdir()
            target.mkdir()
            write_source_agent(source, "code-reviewer", references_skill=True)
            write_source_skill(source, "code-reviewer")

            result = self._install(
                source, target, skills=["code-reviewer"], agents=["code-reviewer"]
            )
            self.assertTrue(result.ok)
            self.assertEqual(result.warnings, [])
            message = installer.format_result(result, uninstall=False)
            self.assertNotIn("Warnings:", message)

    def test_plain_agent_no_warning(self) -> None:
        """An agent whose body references no .agents/skills/ path never
        warns (non-checker agents)."""
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            target = Path(tmp) / "target"
            source.mkdir()
            target.mkdir()
            write_source_agent(source, "standalone-agent", references_skill=False)

            result = self._install(source, target, agents=["standalone-agent"])
            self.assertTrue(result.ok)
            self.assertEqual(result.warnings, [])

    def test_skill_only_install_never_warns(self) -> None:
        """cr-004: the warning fires only for agent installs. A skill-only
        pass (even one whose target happens to contain an agent file with a
        dangling reference) adds no warning — the helper runs in the agents
        loop only, with agent semantics."""
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            target = Path(tmp) / "target"
            source.mkdir()
            target.mkdir()
            # A pre-existing agent in the target with a dangling reference —
            # not part of this install.
            write_source_agent(target, "code-reviewer", references_skill=True)
            write_source_skill(source, "unrelated-skill")

            result = self._install(source, target, skills=["unrelated-skill"])
            self.assertTrue(result.ok)
            self.assertEqual(
                result.warnings,
                [],
                "skill-only installs must not emit agent warnings",
            )

    def test_command_and_guideline_loops_have_no_warning_logic(self) -> None:
        """cr-004 structural pin: warn_unpaired_agent_skill is referenced
        exactly once — the agents loop. The dead copies are gone."""
        source = (REPO_ROOT / "tools" / "installer.py").read_text(encoding="utf-8")
        self.assertEqual(
            source.count("warn_unpaired_agent_skill("),
            2,
            "expected the def plus exactly one call site (agents loop only)",
        )
        self.assertEqual(source.count("ar-012:"), 2,
                         "the ar-012 comment should live in the helper and its call site")

    def test_agent_warns_for_secondary_referenced_skill(self) -> None:
        """C-09: warn when an agent's paired skill is installed, but another
        skill referenced in its body (e.g. dev-workflow-orchestrator) is missing."""
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            target = Path(tmp) / "target"
            source.mkdir()
            target.mkdir()
            write_source_skill(source, "code-reviewer")
            for rel in (
                Path(".claude") / "agents" / "code-reviewer.md",
                Path(".github") / "agents" / "code-reviewer.agent.md",
            ):
                path = source / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(
                    "---\nname: code-reviewer\ndescription: checker\n---\n\n"
                    "Read `.agents/skills/dev-workflow-orchestrator/references/checker-subagent-contract.md`.\n"
                    "Criteria: `.agents/skills/code-reviewer/SKILL.md`.\n",
                    encoding="utf-8",
                )

            result = self._install(
                source, target, skills=["code-reviewer"], agents=["code-reviewer"]
            )
            self.assertTrue(result.ok)
            self.assertEqual(len(result.warnings), 1, result.warnings)
            self.assertIn("--skills dev-workflow-orchestrator", result.warnings[0])


if __name__ == "__main__":
    unittest.main()
