"""Tests for tools/install_all.py — bulk regeneration from bootstrap sources."""

from __future__ import annotations

import importlib.util
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
INSTALL_ALL_PATH = TOOLS_DIR / "install_all.py"
REPO_ROOT = TOOLS_DIR.parent

CREATOR_SKILLS = ("skill-creator", "agent-creator", "command-creator")


def load_install_all_module():
    spec = importlib.util.spec_from_file_location("install_all_under_test", INSTALL_ALL_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load module from {INSTALL_ALL_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["install_all_under_test"] = module
    spec.loader.exec_module(module)
    return module


mod = load_install_all_module()


def write_skill(root: Path, name: str, *, description: str = "test skill") -> None:
    skill_md = root / "skills" / name / "SKILL.md"
    skill_md.parent.mkdir(parents=True, exist_ok=True)
    skill_md.write_text(
        f"---\nname: {name}\ndescription: {description}\n---\n\n# {name}\n",
        encoding="utf-8",
    )


def write_agent(root: Path, name: str) -> None:
    agent_md = root / "agents" / name / "AGENT.md"
    agent_md.parent.mkdir(parents=True, exist_ok=True)
    agent_md.write_text(
        f"---\nname: {name}\ndescription: {name} agent\n---\n\n# {name}\n",
        encoding="utf-8",
    )


def write_command(root: Path, name: str) -> None:
    command_md = root / "commands" / name / "COMMAND.md"
    command_md.parent.mkdir(parents=True, exist_ok=True)
    command_md.write_text(
        f"---\nname: {name}\ndescription: {name} command — use when the user explicitly invokes /{name}.\n---\n\n# {name}\n",
        encoding="utf-8",
    )


def seed_creator_scripts(root: Path) -> None:
    """Copy the real creator script dirs into the fixture root.

    load_installer_module resolves them under <root>/skills/<creator>/scripts,
    so a fixture root needs the same layout the real repository has.
    """
    for creator in CREATOR_SKILLS:
        shutil.copytree(
            REPO_ROOT / "skills" / creator / "scripts",
            root / "skills" / creator / "scripts",
            ignore=shutil.ignore_patterns("__pycache__"),
        )


class InstallAllTests(unittest.TestCase):
    def setUp(self) -> None:
        self._original_root = mod.REPO_ROOT
        self._tmp = tempfile.TemporaryDirectory(prefix="install-all-")
        self.root = Path(self._tmp.name)
        seed_creator_scripts(self.root)
        mod.REPO_ROOT = self.root

    def tearDown(self) -> None:
        mod.REPO_ROOT = self._original_root
        self._tmp.cleanup()

    def test_regenerates_all_installed_output(self) -> None:
        write_skill(self.root, "alpha")
        write_agent(self.root, "reviewer")
        write_command(self.root, "ship")

        failures = mod.install_all(self.root)

        self.assertEqual(failures, 0)
        self.assertTrue(
            (self.root / ".agents" / "skills" / "alpha" / "SKILL.md").is_file()
        )
        self.assertTrue(
            (self.root / ".claude" / "agents" / "reviewer.md").is_file()
        )
        self.assertTrue(
            (self.root / ".github" / "agents" / "reviewer.agent.md").is_file()
        )
        command_skill = (
            self.root / ".agents" / "skills" / "cmd-ship" / "SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertIn("disable-model-invocation: true", command_skill)

    def test_failed_member_is_reported_and_others_install(self) -> None:
        write_skill(self.root, "good")
        # Missing frontmatter description fails source verification.
        write_skill(self.root, "bad", description="")

        failures = mod.install_all(self.root)

        self.assertEqual(failures, 1)
        self.assertTrue(
            (self.root / ".agents" / "skills" / "good" / "SKILL.md").is_file()
        )
        self.assertFalse(
            (self.root / ".agents" / "skills" / "bad").exists()
        )

    def test_creator_module_loads_do_not_leak_sibling_imports(self) -> None:
        # Regression: a cached quick_validate from one creator's scripts dir
        # broke the next creator's bare-name imports (validate_agent missing).
        for creator in CREATOR_SKILLS:
            module = mod.load_installer_module(creator)
            expected_dir = (
                self.root / "skills" / creator / "scripts"
            ).resolve()
            self.assertEqual(Path(module.__file__).resolve().parent, expected_dir)

    def test_no_overwrite_refuses_existing_install(self) -> None:
        write_skill(self.root, "alpha")
        self.assertEqual(mod.install_all(self.root), 0)
        installed_md = (
            self.root / ".agents" / "skills" / "alpha" / "SKILL.md"
        )
        original = installed_md.read_text(encoding="utf-8")

        # A modified source must not clobber the existing install.
        write_skill(self.root, "alpha", description="changed description")
        failures = mod.install_all(self.root, overwrite=False)

        self.assertEqual(failures, 1)
        self.assertEqual(installed_md.read_text(encoding="utf-8"), original)

    def test_skip_validate_installs_invalid_package(self) -> None:
        # Angle brackets in the description pass source verification but
        # fail quick_validate. The install copy is written before
        # validation runs, so the contract difference is the failure count.
        write_skill(self.root, "bracketed", description="uses <angle> brackets")

        failures = mod.install_all(self.root)
        self.assertEqual(failures, 1)

        failures = mod.install_all(self.root, skip_validate=True)
        self.assertEqual(failures, 0)
        self.assertTrue(
            (self.root / ".agents" / "skills" / "bracketed" / "SKILL.md").is_file()
        )

    def test_main_rejects_foreign_root(self) -> None:
        foreign = self.root / "elsewhere"
        foreign.mkdir()

        exit_code = mod.main(["--root", str(foreign)])

        self.assertEqual(exit_code, 2)

    def test_kind_level_load_failure_is_counted_not_fatal(self) -> None:
        # Regression: a broken creator scripts dir used to crash the whole
        # run with an uncaught ImportError, skipping the remaining kinds.
        write_skill(self.root, "alpha")
        write_command(self.root, "ship")
        shutil.rmtree(self.root / "skills" / "agent-creator" / "scripts")

        failures = mod.install_all(self.root)

        self.assertEqual(failures, 1)
        self.assertTrue(
            (self.root / ".agents" / "skills" / "alpha" / "SKILL.md").is_file()
        )
        self.assertTrue(
            (self.root / ".agents" / "skills" / "cmd-ship" / "SKILL.md").is_file()
        )


if __name__ == "__main__":
    unittest.main()
