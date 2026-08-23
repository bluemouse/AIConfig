#!/usr/bin/env python3
"""Tests for the --dev-workflow harness install/uninstall in installer.py."""

from __future__ import annotations

import importlib.util
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
    shared = root / ".shared" / "skills" / name / "SKILL.md"
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
    shared = root / ".shared" / "commands" / f"{name}.md"
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
    scripts = root / "tools" / name
    scripts.mkdir(parents=True, exist_ok=True)
    (scripts / "validate_phase.py").write_text("# validate_phase\n", encoding="utf-8")
    (scripts / "check_pre_phase.py").write_text("# check_pre_phase\n", encoding="utf-8")
    checks = scripts / "checks"
    checks.mkdir(parents=True, exist_ok=True)
    (checks / "__init__.py").write_text("", encoding="utf-8")
    (checks / "mode_checks.py").write_text("# mode_checks\n", encoding="utf-8")


def write_full_harness_source(root: Path) -> None:
    """Write the full dev-workflow harness into a source root."""
    for skill in mod.DEV_WORKFLOW_SKILLS:
        write_source_skill(root, skill)
    for command in mod.DEV_WORKFLOW_COMMANDS:
        write_source_command(root, command)
    write_source_scripts(root)


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
                "finding-resolver",
                "code-reviewer",
                "commit-message-writer",
            ),
        )
        self.assertEqual(mod.DEV_WORKFLOW_COMMANDS, ("dev-workflow",))
        self.assertEqual(mod.DEV_WORKFLOW_SCRIPTS, ("dev-workflow",))


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
            scripts = target / "tools" / "dev-workflow"
            self.assertTrue(scripts.is_dir())
            self.assertTrue((scripts / "validate_phase.py").is_file())
            self.assertTrue((scripts / "checks" / "__init__.py").is_file())
            self.assertIn("tools/dev-workflow", result.installed)

    def test_install_scripts_skips_existing_without_override(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            target = Path(tmp) / "target"
            write_source_scripts(source)
            stale = target / "tools" / "dev-workflow" / "stale.txt"
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
            self.assertIn("tools/dev-workflow", result.skipped)
            self.assertEqual(stale.read_text(encoding="utf-8"), "stale")

    def test_install_scripts_override_replaces(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            target = Path(tmp) / "target"
            write_source_scripts(source)
            stale = target / "tools" / "dev-workflow" / "stale.txt"
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
            self.assertIn("tools/dev-workflow", result.installed)
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
            self.assertFalse((target / "tools" / "dev-workflow").exists())
            self.assertIn("tools/dev-workflow", result.removed)

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
                "code-reviewer",
                "commit-message-writer",
                "dev-workflow-orchestrator",
                "finding-resolver",
                "implementation-auditor",
                "plan-executor",
                "plan-guide",
                "plan-reviewer",
                "prompt-clarifier",
                "research-guide",
                "research-reviewer",
            ],
        )
        self.assertEqual(selection.commands, ["dev-workflow"])
        self.assertEqual(selection.scripts, ["dev-workflow"])
        self.assertEqual(selection.agents, [])

    def test_install_harness_via_explicit_params(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            target = Path(tmp) / "target"
            write_full_harness_source(source)

            result = mod.install_items(
                source_root=source,
                target_root=target,
                skills=list(mod.DEV_WORKFLOW_SKILLS),
                agents=[],
                commands=list(mod.DEV_WORKFLOW_COMMANDS),
                scripts=list(mod.DEV_WORKFLOW_SCRIPTS),
                override=False,
            )

            self.assertTrue(result.ok, result.errors)
            for skill in mod.DEV_WORKFLOW_SKILLS:
                self.assertTrue((target / ".shared" / "skills" / skill / "SKILL.md").is_file())
            self.assertTrue((target / ".shared" / "commands" / "dev-workflow.md").is_file())
            self.assertTrue((target / "tools" / "dev-workflow" / "validate_phase.py").is_file())

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


if __name__ == "__main__":
    unittest.main()
