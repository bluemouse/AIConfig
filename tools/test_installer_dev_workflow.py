#!/usr/bin/env python3
"""Tests for the --dev-workflow harness install/uninstall in installer.py."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
INSTALLER_PATH = TOOLS_DIR / "installer.py"


def load_installer_module():
    spec = importlib.util.spec_from_file_location("installer_dev_workflow", INSTALLER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load module from {INSTALLER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["installer_dev_workflow"] = module
    spec.loader.exec_module(module)
    return module


mod = load_installer_module()


def write_source_skill(root: Path, name: str) -> None:
    """Write a minimal skill (shared dir + SKILL.md + three tool wrappers)."""
    shared = root / ".ai" / "skills" / name / "SKILL.md"
    shared.parent.mkdir(parents=True, exist_ok=True)
    shared.write_text(
        f"---\nname: {name}\ndescription: {name} skill\n---\n\n# {name}\n",
        encoding="utf-8",
    )
    for rel in (
        f".cursor/skills/{name}/SKILL.md",
        f".claude/skills/{name}/SKILL.md",
        f".github/skills/{name}/SKILL.md",
    ):
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"# {name}\n", encoding="utf-8")


def write_source_command(root: Path, name: str) -> None:
    """Write a minimal command (shared file + three tool wrappers)."""
    shared = root / ".ai" / "commands" / f"{name}.md"
    shared.parent.mkdir(parents=True, exist_ok=True)
    shared.write_text(
        f"---\nname: {name}\ndescription: {name} command\n---\n\n# {name}\n",
        encoding="utf-8",
    )
    for rel in (
        f".cursor/commands/{name}.md",
        f".claude/commands/{name}.md",
        f".github/prompts/{name}.prompt.md",
    ):
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"# {name}\n", encoding="utf-8")


def write_source_scripts(root: Path, name: str = "dev-workflow") -> None:
    """Write a minimal tools/<name>/ scripts tree with a checks/ subpackage."""
    scripts = root / ".ai" / "tools" / name
    scripts.mkdir(parents=True, exist_ok=True)
    (scripts / "validate_phase.py").write_text("# validate_phase\n", encoding="utf-8")
    (scripts / "check_pre_phase.py").write_text("# check_pre_phase\n", encoding="utf-8")
    checks = scripts / "checks"
    checks.mkdir(parents=True, exist_ok=True)
    (checks / "__init__.py").write_text("", encoding="utf-8")
    (checks / "mode_checks.py").write_text("# mode_checks\n", encoding="utf-8")


def write_source_agent(root: Path, name: str) -> None:
    """Write a minimal agent (shared file + three tool wrappers).

    Paths mirror the installer's TOOL_AGENT_FILES and SHARED_AGENT_FILE:
    - .ai/agents/<name>.md
    - .cursor/agents/<name>.md
    - .claude/agents/<name>.md
    - .github/agents/<name>.agent.md  (note the .agent.md suffix for Copilot)
    """
    shared = root / ".ai" / "agents" / f"{name}.md"
    shared.parent.mkdir(parents=True, exist_ok=True)
    shared.write_text(
        f"---\nname: {name}\ndescription: {name} agent\n---\n\n# {name}\n",
        encoding="utf-8",
    )
    for rel in (
        f".cursor/agents/{name}.md",
        f".claude/agents/{name}.md",
        f".github/agents/{name}.agent.md",
    ):
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"# {name}\n", encoding="utf-8")


def write_full_harness_source(root: Path) -> None:
    """Write the full dev-workflow harness into a source root."""
    for skill in mod.DEV_WORKFLOW_SKILLS:
        write_source_skill(root, skill)
    for command in mod.DEV_WORKFLOW_COMMANDS:
        write_source_command(root, command)
    write_source_scripts(root)
    for agent in mod.DEV_WORKFLOW_AGENTS:
        write_source_agent(root, agent)


class DevWorkflowConstantsTests(unittest.TestCase):
    def test_harness_constants(self) -> None:
        self.assertEqual(
            mod.DEV_WORKFLOW_SKILLS,
            (
                "dev-workflow-orchestrator",
                "prompt-clarifier",
                "research-guide",
                "research-reviewer",
                "plan-guide",
                "plan-reviewer",
                "plan-executor",
                "implementation-auditor",
                "code-review-resolver",
                "code-reviewer",
                "commit-message-writer",
            ),
        )
        self.assertEqual(
            mod.DEV_WORKFLOW_COMMANDS,
            (
                "dev-workflow",
                "dev-workflow-research",
                "dev-workflow-plan",
                "dev-workflow-implement",
                "dev-workflow-review",
            ),
        )
        self.assertEqual(mod.DEV_WORKFLOW_SCRIPTS, ("dev-workflow",))
        self.assertEqual(
            mod.DEV_WORKFLOW_AGENTS,
            (
                "research-reviewer",
                "plan-reviewer",
                "implementation-auditor",
                "code-reviewer",
            ),
        )


class ScriptsInstallTests(unittest.TestCase):
    def test_install_scripts_copies_directory_tree(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            target = Path(tmp) / "target"
            write_source_scripts(source)

            result = mod.install_items(
                source_root=source,
                target_root=target,
                skills=[],
                agents=[],
                commands=[],
                scripts=["dev-workflow"],
                override=False,
            )

            self.assertTrue(result.ok, result.errors)
            scripts = target / ".ai" / "tools" / "dev-workflow"
            self.assertTrue(scripts.is_dir())
            self.assertTrue((scripts / "validate_phase.py").is_file())
            self.assertTrue((scripts / "checks" / "__init__.py").is_file())
            self.assertIn(".ai/tools/dev-workflow", result.installed)

    def test_install_scripts_skips_existing_without_override(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            target = Path(tmp) / "target"
            write_source_scripts(source)
            stale = target / ".ai" / "tools" / "dev-workflow" / "stale.txt"
            stale.parent.mkdir(parents=True, exist_ok=True)
            stale.write_text("stale", encoding="utf-8")

            result = mod.install_items(
                source_root=source,
                target_root=target,
                skills=[],
                agents=[],
                commands=[],
                scripts=["dev-workflow"],
                override=False,
            )

            self.assertTrue(result.ok, result.errors)
            self.assertIn(".ai/tools/dev-workflow", result.skipped)
            self.assertEqual(stale.read_text(encoding="utf-8"), "stale")

    def test_install_scripts_override_replaces(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            target = Path(tmp) / "target"
            write_source_scripts(source)
            stale = target / ".ai" / "tools" / "dev-workflow" / "stale.txt"
            stale.parent.mkdir(parents=True, exist_ok=True)
            stale.write_text("stale", encoding="utf-8")

            result = mod.install_items(
                source_root=source,
                target_root=target,
                skills=[],
                agents=[],
                commands=[],
                scripts=["dev-workflow"],
                override=True,
            )

            self.assertTrue(result.ok, result.errors)
            self.assertIn(".ai/tools/dev-workflow", result.installed)
            self.assertFalse(stale.exists())

    def test_install_scripts_missing_source_records_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            target = Path(tmp) / "target"
            source.mkdir(parents=True, exist_ok=True)

            result = mod.install_items(
                source_root=source,
                target_root=target,
                skills=[],
                agents=[],
                commands=[],
                scripts=["dev-workflow"],
                override=False,
            )

            self.assertFalse(result.ok)
            self.assertTrue(
                any("scripts dev-workflow" in msg for msg in result.errors),
                result.errors,
            )


class ScriptsUninstallTests(unittest.TestCase):
    def test_uninstall_scripts_removes_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            target = Path(tmp) / "target"
            write_source_scripts(source)

            mod.install_items(
                source_root=source,
                target_root=target,
                skills=[],
                agents=[],
                commands=[],
                scripts=["dev-workflow"],
                override=False,
            )

            result = mod.uninstall_items(
                target_root=target,
                skills=[],
                agents=[],
                commands=[],
                scripts=["dev-workflow"],
            )

            self.assertTrue(result.ok, result.errors)
            self.assertFalse((target / ".ai" / "tools" / "dev-workflow").exists())
            self.assertIn(".ai/tools/dev-workflow", result.removed)

    def test_uninstall_scripts_when_not_installed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir(parents=True, exist_ok=True)

            result = mod.uninstall_items(
                target_root=target,
                skills=[],
                agents=[],
                commands=[],
                scripts=["dev-workflow"],
            )

            self.assertTrue(result.ok, result.errors)
            self.assertEqual(result.removed, [])


class DevWorkflowBundleTests(unittest.TestCase):
    def test_resolve_dev_workflow_harness_bundle(self) -> None:
        selection = mod.resolve_bundle(["dev-workflow-harness"])
        self.assertEqual(
            selection.skills,
            [
                "code-review-resolver",
                "code-reviewer",
                "commit-message-writer",
                "dev-workflow-orchestrator",
                "implementation-auditor",
                "plan-executor",
                "plan-guide",
                "plan-reviewer",
                "prompt-clarifier",
                "research-guide",
                "research-reviewer",
            ],
        )
        self.assertEqual(
            selection.commands,
            [
                "dev-workflow",
                "dev-workflow-implement",
                "dev-workflow-plan",
                "dev-workflow-research",
                "dev-workflow-review",
            ],
        )
        self.assertEqual(selection.scripts, ["dev-workflow"])
        self.assertEqual(
            selection.agents,
            [
                "code-reviewer",
                "implementation-auditor",
                "plan-reviewer",
                "research-reviewer",
            ],
        )

    def test_dev_workflow_bundle_includes_agents_in_bundles_json(self) -> None:
        """t-013: the dev-workflow-harness bundle in bundles.json has an agents key."""
        import json

        bundles_path = TOOLS_DIR / "bundles.json"
        payload = json.loads(bundles_path.read_text(encoding="utf-8"))
        harness = next(
            b for b in payload["bundles"] if b["id"] == "dev-workflow-harness"
        )
        self.assertIn("agents", harness)
        self.assertEqual(
            sorted(harness["agents"]),
            ["code-reviewer", "implementation-auditor", "plan-reviewer", "research-reviewer"],
        )

    def test_install_harness_via_explicit_params(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            target = Path(tmp) / "target"
            write_full_harness_source(source)

            result = mod.install_items(
                source_root=source,
                target_root=target,
                skills=list(mod.DEV_WORKFLOW_SKILLS),
                agents=list(mod.DEV_WORKFLOW_AGENTS),
                commands=list(mod.DEV_WORKFLOW_COMMANDS),
                scripts=list(mod.DEV_WORKFLOW_SCRIPTS),
                override=False,
            )

            self.assertTrue(result.ok, result.errors)
            for skill in mod.DEV_WORKFLOW_SKILLS:
                self.assertTrue((target / ".ai" / "skills" / skill / "SKILL.md").is_file())
            self.assertTrue((target / ".ai" / "commands" / "dev-workflow.md").is_file())
            self.assertTrue((target / ".ai" / "tools" / "dev-workflow" / "validate_phase.py").is_file())
            # t-014: agents are installed via --dev-workflow
            for agent in mod.DEV_WORKFLOW_AGENTS:
                self.assertTrue((target / ".ai" / "agents" / f"{agent}.md").is_file())
                self.assertTrue((target / ".cursor" / "agents" / f"{agent}.md").is_file())
                self.assertTrue((target / ".claude" / "agents" / f"{agent}.md").is_file())
                self.assertTrue((target / ".github" / "agents" / f"{agent}.agent.md").is_file())

    def test_uninstall_harness_removes_agents(self) -> None:
        """Uninstalling the harness removes agent files from the target."""
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            target = Path(tmp) / "target"
            write_full_harness_source(source)

            install_result = mod.install_items(
                source_root=source,
                target_root=target,
                skills=list(mod.DEV_WORKFLOW_SKILLS),
                agents=list(mod.DEV_WORKFLOW_AGENTS),
                commands=list(mod.DEV_WORKFLOW_COMMANDS),
                scripts=list(mod.DEV_WORKFLOW_SCRIPTS),
                override=False,
            )
            self.assertTrue(install_result.ok, install_result.errors)

            uninstall_result = mod.uninstall_items(
                target_root=target,
                skills=list(mod.DEV_WORKFLOW_SKILLS),
                agents=list(mod.DEV_WORKFLOW_AGENTS),
                commands=list(mod.DEV_WORKFLOW_COMMANDS),
                scripts=list(mod.DEV_WORKFLOW_SCRIPTS),
            )
            self.assertTrue(uninstall_result.ok, uninstall_result.errors)
            for agent in mod.DEV_WORKFLOW_AGENTS:
                self.assertFalse(
                    (target / ".ai" / "agents" / f"{agent}.md").is_file(),
                    f"Agent {agent} shared file not removed by uninstall",
                )
                self.assertFalse(
                    (target / ".cursor" / "agents" / f"{agent}.md").is_file(),
                    f"Agent {agent} cursor wrapper not removed by uninstall",
                )

    def test_override_replaces_agent_files(self) -> None:
        """--override replaces existing agent files in the target."""
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            target = Path(tmp) / "target"
            write_full_harness_source(source)

            # First install
            result1 = mod.install_items(
                source_root=source,
                target_root=target,
                skills=[],
                agents=list(mod.DEV_WORKFLOW_AGENTS),
                commands=[],
                scripts=[],
                override=False,
            )
            self.assertTrue(result1.ok, result1.errors)

            # Modify a target agent file to simulate stale content
            stale_path = target / ".ai" / "agents" / "implementation-auditor.md"
            stale_path.write_text("STALE CONTENT", encoding="utf-8")

            # Override install
            result2 = mod.install_items(
                source_root=source,
                target_root=target,
                skills=[],
                agents=list(mod.DEV_WORKFLOW_AGENTS),
                commands=[],
                scripts=[],
                override=True,
            )
            self.assertTrue(result2.ok, result2.errors)
            self.assertNotEqual(
                stale_path.read_text(encoding="utf-8"),
                "STALE CONTENT",
                "Override did not replace stale agent file",
            )

    def test_compose_dev_workflow_with_agents(self) -> None:
        """--dev-workflow composes with --agents in a single invocation."""
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            target = Path(tmp) / "target"
            write_full_harness_source(source)

            result = mod.install_items(
                source_root=source,
                target_root=target,
                skills=list(mod.DEV_WORKFLOW_SKILLS),
                agents=list(mod.DEV_WORKFLOW_AGENTS),
                commands=list(mod.DEV_WORKFLOW_COMMANDS),
                scripts=list(mod.DEV_WORKFLOW_SCRIPTS),
                override=False,
            )
            self.assertTrue(result.ok, result.errors)
            for agent in mod.DEV_WORKFLOW_AGENTS:
                self.assertTrue(
                    (target / ".ai" / "agents" / f"{agent}.md").is_file(),
                    f"Composed install did not install agent {agent}",
                )

    def test_run_operation_scripts_only_does_not_raise(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            code, message = mod.run_operation(
                target=target,
                skills=[],
                agents=[],
                commands=[],
                scripts=["dev-workflow"],
                uninstall=False,
                override=False,
            )
            self.assertIsInstance(message, str)

    def test_run_operation_no_selection_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            with self.assertRaises(mod.InstallerError) as ctx:
                mod.run_operation(
                    target=target,
                    skills=[],
                    agents=[],
                    commands=[],
                    scripts=[],
                    uninstall=False,
                    override=False,
                )
            self.assertIn("scripts", str(ctx.exception))


class BundlesJsonPhaseCommandsTests(unittest.TestCase):
    """Tests that bundles.json dev-workflow-harness includes the per-phase commands."""

    def test_bundles_json_dev_workflow_harness_commands_includes_phases(self) -> None:
        bundles_path = TOOLS_DIR / "bundles.json"
        with bundles_path.open(encoding="utf-8") as f:
            data = json.load(f)

        harness = next(
            (b for b in data["bundles"] if b["id"] == "dev-workflow-harness"),
            None,
        )
        self.assertIsNotNone(harness, "dev-workflow-harness bundle not found")
        assert harness is not None  # for type checkers
        self.assertEqual(
            harness["commands"],
            [
                "dev-workflow",
                "dev-workflow-research",
                "dev-workflow-plan",
                "dev-workflow-implement",
                "dev-workflow-review",
            ],
        )


class PhaseCommandsInstallTests(unittest.TestCase):
    """Integration tests for install/uninstall/override of the per-phase commands."""

    def test_install_dev_workflow_harness_installs_phase_commands(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            target = Path(tmp) / "target"
            write_full_harness_source(source)

            result = mod.install_items(
                source_root=source,
                target_root=target,
                skills=[],
                agents=[],
                commands=list(mod.DEV_WORKFLOW_COMMANDS),
                scripts=[],
                override=False,
            )

            self.assertTrue(result.ok, result.errors)
            for name in mod.DEV_WORKFLOW_COMMANDS:
                for rel in (
                    f".ai/commands/{name}.md",
                    f".cursor/commands/{name}.md",
                    f".claude/commands/{name}.md",
                    f".github/prompts/{name}.prompt.md",
                ):
                    self.assertTrue(
                        (target / rel).is_file(),
                        f"Expected installed command file missing: {rel}",
                    )

    def test_uninstall_dev_workflow_harness_removes_phase_commands(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            target = Path(tmp) / "target"
            write_full_harness_source(source)

            mod.install_items(
                source_root=source,
                target_root=target,
                skills=[],
                agents=[],
                commands=list(mod.DEV_WORKFLOW_COMMANDS),
                scripts=[],
                override=False,
            )

            result = mod.uninstall_items(
                target_root=target,
                skills=[],
                agents=[],
                commands=list(mod.DEV_WORKFLOW_COMMANDS),
                scripts=[],
            )

            self.assertTrue(result.ok, result.errors)
            for name in mod.DEV_WORKFLOW_COMMANDS:
                for rel in (
                    f".ai/commands/{name}.md",
                    f".cursor/commands/{name}.md",
                    f".claude/commands/{name}.md",
                    f".github/prompts/{name}.prompt.md",
                ):
                    self.assertFalse(
                        (target / rel).exists(),
                        f"Command file should be removed after uninstall: {rel}",
                    )

    def test_install_dev_workflow_harness_override_replaces_phase_commands(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            target = Path(tmp) / "target"
            write_full_harness_source(source)

            mod.install_items(
                source_root=source,
                target_root=target,
                skills=[],
                agents=[],
                commands=list(mod.DEV_WORKFLOW_COMMANDS),
                scripts=[],
                override=False,
            )

            # Write a stale marker into one of the new command paths.
            stale = target / ".ai" / "commands" / "dev-workflow-research.md"
            stale.write_text("stale content", encoding="utf-8")

            result = mod.install_items(
                source_root=source,
                target_root=target,
                skills=[],
                agents=[],
                commands=list(mod.DEV_WORKFLOW_COMMANDS),
                scripts=[],
                override=True,
            )

            self.assertTrue(result.ok, result.errors)
            self.assertNotEqual(
                stale.read_text(encoding="utf-8"),
                "stale content",
                "Override should replace stale content",
            )


if __name__ == "__main__":
    unittest.main()
