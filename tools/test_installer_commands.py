#!/usr/bin/env python3
"""Tests for command install/uninstall in installer.py."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
INSTALLER_PATH = TOOLS_DIR / "installer.py"


def load_installer_module():
    spec = importlib.util.spec_from_file_location("installer_commands", INSTALLER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load module from {INSTALLER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["installer_commands"] = module
    spec.loader.exec_module(module)
    return module


mod = load_installer_module()


class CommandDiscoveryTests(unittest.TestCase):
    def test_discover_commands_includes_git_commit(self) -> None:
        commands = mod.discover_commands()
        self.assertIn("git-commit", commands)

    def test_load_command_descriptions(self) -> None:
        descriptions = mod.load_command_descriptions(["git-commit"])
        self.assertIn("git-commit", descriptions)
        self.assertIn("commit-message-writer", descriptions["git-commit"])


class CommandInstallTests(unittest.TestCase):
    def _write_source_command(self, root: Path, name: str) -> None:
        shared = root / ".shared" / "commands" / f"{name}.md"
        shared.parent.mkdir(parents=True, exist_ok=True)
        shared.write_text(
            f"---\nname: {name}\ndescription: {name} command\n---\n\n# {name}\n",
            encoding="utf-8",
        )
        cursor = root / ".cursor" / "commands" / f"{name}.md"
        cursor.parent.mkdir(parents=True, exist_ok=True)
        cursor.write_text(f"# {name}\n", encoding="utf-8")
        claude = root / ".claude" / "commands" / f"{name}.md"
        claude.parent.mkdir(parents=True, exist_ok=True)
        claude.write_text(f"---\nname: {name}\n---\n\n# {name}\n", encoding="utf-8")
        github = root / ".github" / "prompts" / f"{name}.prompt.md"
        github.parent.mkdir(parents=True, exist_ok=True)
        github.write_text(f"---\nname: {name}\n---\n\n# {name}\n", encoding="utf-8")

    def test_install_command_copies_all_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            target = Path(tmp) / "target"
            self._write_source_command(source, "demo-command")

            result = mod.install_items(
                source_root=source,
                target_root=target,
                skills=[],
                agents=[],
                commands=["demo-command"],
                override=False,
            )

            self.assertTrue(result.ok, result.errors)
            self.assertTrue((target / ".shared/commands/demo-command.md").is_file())
            self.assertTrue((target / ".cursor/commands/demo-command.md").is_file())
            self.assertTrue((target / ".claude/commands/demo-command.md").is_file())
            self.assertTrue((target / ".github/prompts/demo-command.prompt.md").is_file())

    def test_install_command_skips_existing_without_override(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            target = Path(tmp) / "target"
            self._write_source_command(source, "demo-command")
            stale = target / ".shared/commands/demo-command.md"
            stale.parent.mkdir(parents=True, exist_ok=True)
            stale.write_text("stale", encoding="utf-8")

            result = mod.install_items(
                source_root=source,
                target_root=target,
                skills=[],
                agents=[],
                commands=["demo-command"],
                override=False,
            )

            self.assertTrue(result.ok, result.errors)
            self.assertIn(".shared/commands/demo-command.md", result.skipped)
            self.assertEqual(stale.read_text(encoding="utf-8"), "stale")

    def test_uninstall_command_removes_all_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            self._write_source_command(target, "demo-command")

            result = mod.uninstall_items(
                target_root=target,
                skills=[],
                agents=[],
                commands=["demo-command"],
            )

            self.assertTrue(result.ok, result.errors)
            self.assertFalse((target / ".shared/commands/demo-command.md").exists())
            self.assertFalse((target / ".cursor/commands/demo-command.md").exists())
            self.assertFalse((target / ".claude/commands/demo-command.md").exists())
            self.assertFalse((target / ".github/prompts/demo-command.prompt.md").exists())

    def test_run_operation_requires_selection(self) -> None:
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
                )
            self.assertIn("skill, agent, or command", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
