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


def write_source_scripts(root: Path) -> None:
    """Write a minimal tools/dev-workflow/ scripts tree with a checks/ subpackage."""
    scripts = root / "tools" / "dev-workflow"
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
        self.assertEqual(mod.DEV_WORKFLOW_SKILLS, ("dev-workflow-orchestrator", "finding-resolver"))
        self.assertEqual(mod.DEV_WORKFLOW_COMMANDS, ("dev-workflow",))
        self.assertEqual(mod.DEV_WORKFLOW_SCRIPTS_REL, "tools/dev-workflow")


class DevWorkflowInstallTests(unittest.TestCase):
    def test_install_dev_workflow_copies_all_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            target = Path(tmp) / "target"
            write_full_harness_source(source)

            result = mod.install_items(
                source_root=source,
                target_root=target,
                skills=[],
                agents=[],
                commands=[],
                override=False,
                dev_workflow=True,
            )

            self.assertTrue(result.ok, result.errors)
            # Skills: shared + three tool wrappers each.
            for skill in mod.DEV_WORKFLOW_SKILLS:
                self.assertTrue((target / ".shared" / "skills" / skill / "SKILL.md").is_file())
                self.assertTrue((target / ".cursor" / "skills" / skill / "SKILL.md").is_file())
                self.assertTrue((target / ".claude" / "skills" / skill / "SKILL.md").is_file())
                self.assertTrue((target / ".github" / "skills" / skill / "SKILL.md").is_file())
            # Command: shared + three tool wrappers.
            self.assertTrue((target / ".shared" / "commands" / "dev-workflow.md").is_file())
            self.assertTrue((target / ".cursor" / "commands" / "dev-workflow.md").is_file())
            self.assertTrue((target / ".claude" / "commands" / "dev-workflow.md").is_file())
            self.assertTrue((target / ".github" / "prompts" / "dev-workflow.prompt.md").is_file())
            # Scripts: directory tree with checks/ subpackage.
            scripts = target / "tools" / "dev-workflow"
            self.assertTrue(scripts.is_dir())
            self.assertTrue((scripts / "validate_phase.py").is_file())
            self.assertTrue((scripts / "checks" / "__init__.py").is_file())
            self.assertTrue((scripts / "checks" / "mode_checks.py").is_file())
            self.assertIn("tools/dev-workflow", result.installed)

    def test_install_dev_workflow_skips_existing_scripts_without_override(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            target = Path(tmp) / "target"
            write_full_harness_source(source)
            stale = target / "tools" / "dev-workflow" / "stale.txt"
            stale.parent.mkdir(parents=True, exist_ok=True)
            stale.write_text("stale", encoding="utf-8")

            result = mod.install_items(
                source_root=source,
                target_root=target,
                skills=[],
                agents=[],
                commands=[],
                override=False,
                dev_workflow=True,
            )

            self.assertTrue(result.ok, result.errors)
            self.assertIn("tools/dev-workflow", result.skipped)
            # Stale content preserved because override was False.
            self.assertEqual(stale.read_text(encoding="utf-8"), "stale")

    def test_install_dev_workflow_override_replaces_scripts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            target = Path(tmp) / "target"
            write_full_harness_source(source)
            stale = target / "tools" / "dev-workflow" / "stale.txt"
            stale.parent.mkdir(parents=True, exist_ok=True)
            stale.write_text("stale", encoding="utf-8")

            result = mod.install_items(
                source_root=source,
                target_root=target,
                skills=[],
                agents=[],
                commands=[],
                override=True,
                dev_workflow=True,
            )

            self.assertTrue(result.ok, result.errors)
            self.assertIn("tools/dev-workflow", result.installed)
            # Stale file removed because override replaced the directory.
            self.assertFalse(stale.exists())
            self.assertTrue((target / "tools" / "dev-workflow" / "validate_phase.py").is_file())

    def test_install_dev_workflow_missing_scripts_source_records_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            target = Path(tmp) / "target"
            # Write skills and command but NOT the scripts tree.
            for skill in mod.DEV_WORKFLOW_SKILLS:
                write_source_skill(source, skill)
            for command in mod.DEV_WORKFLOW_COMMANDS:
                write_source_command(source, command)

            result = mod.install_items(
                source_root=source,
                target_root=target,
                skills=[],
                agents=[],
                commands=[],
                override=False,
                dev_workflow=True,
            )

            self.assertFalse(result.ok)
            self.assertTrue(
                any("dev-workflow scripts" in msg for msg in result.errors),
                result.errors,
            )

    def test_install_dev_workflow_composes_with_other_skills(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            target = Path(tmp) / "target"
            write_full_harness_source(source)
            write_source_skill(source, "extra-skill")

            result = mod.install_items(
                source_root=source,
                target_root=target,
                skills=["extra-skill"],
                agents=[],
                commands=[],
                override=False,
                dev_workflow=True,
            )

            self.assertTrue(result.ok, result.errors)
            # Both the harness skill and the extra skill are installed.
            self.assertTrue(
                (target / ".shared" / "skills" / "dev-workflow-orchestrator" / "SKILL.md").is_file()
            )
            self.assertTrue((target / ".shared" / "skills" / "extra-skill" / "SKILL.md").is_file())


class DevWorkflowUninstallTests(unittest.TestCase):
    def test_uninstall_dev_workflow_removes_all_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            target = Path(tmp) / "target"
            write_full_harness_source(source)

            mod.install_items(
                source_root=source,
                target_root=target,
                skills=[],
                agents=[],
                commands=[],
                override=False,
                dev_workflow=True,
            )

            result = mod.uninstall_items(
                target_root=target,
                skills=[],
                agents=[],
                commands=[],
                dev_workflow=True,
            )

            self.assertTrue(result.ok, result.errors)
            for skill in mod.DEV_WORKFLOW_SKILLS:
                self.assertFalse((target / ".shared" / "skills" / skill).exists())
                self.assertFalse((target / ".cursor" / "skills" / skill).exists())
                self.assertFalse((target / ".claude" / "skills" / skill).exists())
                self.assertFalse((target / ".github" / "skills" / skill).exists())
            self.assertFalse((target / ".shared" / "commands" / "dev-workflow.md").exists())
            self.assertFalse((target / ".cursor" / "commands" / "dev-workflow.md").exists())
            self.assertFalse((target / ".claude" / "commands" / "dev-workflow.md").exists())
            self.assertFalse((target / ".github" / "prompts" / "dev-workflow.prompt.md").exists())
            self.assertFalse((target / "tools" / "dev-workflow").exists())
            self.assertIn("tools/dev-workflow", result.removed)

    def test_uninstall_dev_workflow_when_not_installed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir(parents=True, exist_ok=True)

            result = mod.uninstall_items(
                target_root=target,
                skills=[],
                agents=[],
                commands=[],
                dev_workflow=True,
            )

            self.assertTrue(result.ok, result.errors)
            # Nothing matched; no errors.
            self.assertEqual(result.removed, [])


class DevWorkflowRunOperationTests(unittest.TestCase):
    def test_run_operation_dev_workflow_only_does_not_raise(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            target = Path(tmp) / "target"
            write_full_harness_source(source)

            code, message = mod.run_operation(
                target=target,
                skills=[],
                agents=[],
                commands=[],
                uninstall=False,
                override=False,
                dev_workflow=True,
            )
            # run_operation uses REPO_ROOT as the source, so the real harness
            # scripts exist; the shared skills/commands may or may not. We only
            # assert the call did not raise and produced a message.
            self.assertEqual(code, 0 if not message or "Errors" not in message else 1)
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
                    uninstall=False,
                    override=False,
                    dev_workflow=False,
                )
            self.assertIn("--dev-workflow", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
