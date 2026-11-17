#!/usr/bin/env python3
"""Tests for the guidelines member kind in installer.py.

Guidelines install as skill packages: the source guidelines/<name>.md is
wrapped into .agents/skills/guidelines-<name>/SKILL.md with `name:
guidelines-<name>` frontmatter injected at install time.
"""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

TOOLS_DIR = Path(__file__).resolve().parent
INSTALLER_PATH = TOOLS_DIR / "installer.py"


def load_installer_module():
    spec = importlib.util.spec_from_file_location("installer_guidelines", INSTALLER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load module from {INSTALLER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["installer_guidelines"] = module
    spec.loader.exec_module(module)
    return module


mod = load_installer_module()

REPO_ROOT = TOOLS_DIR.parent


class RepoGuidelineLayoutTests(unittest.TestCase):
    """The behavioral guideline sources live in guidelines/ at the repo root."""

    def test_repo_guidelines_live_in_guidelines_folder(self) -> None:
        for name in mod.INSTALLABLE_GUIDELINES:
            self.assertTrue(
                (REPO_ROOT / "guidelines" / f"{name}.md").is_file(),
                f"Guideline must live at guidelines/{name}.md",
            )

    def test_repo_guidelines_carry_descriptions(self) -> None:
        for name in mod.INSTALLABLE_GUIDELINES:
            content = (REPO_ROOT / "guidelines" / f"{name}.md").read_text(
                encoding="utf-8"
            )
            self.assertTrue(
                content.startswith("---\n"),
                f"guidelines/{name}.md must carry YAML frontmatter",
            )


def write_source_guideline(root: Path, name: str, text: str) -> None:
    """Write a minimal guideline source file under <root>/guidelines/."""
    path = root / "guidelines" / f"{name}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


GUIDELINE_SOURCE = """---
description: "Load before writing or editing code."
---

# Sample Guideline

Body text for the guideline.
"""


class GuidelineSkillContentTests(unittest.TestCase):
    """The install-time transform: source .md → skill package SKILL.md."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.source_root = Path(self._tmp.name)
        write_source_guideline(self.source_root, "sample", GUIDELINE_SOURCE)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_skill_name_is_prefixed(self) -> None:
        self.assertEqual(mod.guideline_skill_name("sample"), "guidelines-sample")
        self.assertEqual(
            mod.guideline_skill_name("Sample Name"), "guidelines-sample-name"
        )

    def test_content_injects_name_and_keeps_description(self) -> None:
        content = mod.guideline_skill_content(self.source_root, "sample")
        self.assertTrue(content.startswith("---\n"))
        self.assertIn("name: guidelines-sample", content)
        self.assertIn("description:", content)
        self.assertIn("Load before writing or editing code.", content)
        self.assertIn("# Sample Guideline", content)
        self.assertIn("Body text for the guideline.", content)

    def test_content_is_deterministic(self) -> None:
        first = mod.guideline_skill_content(self.source_root, "sample")
        second = mod.guideline_skill_content(self.source_root, "sample")
        self.assertEqual(first, second)

    def test_missing_frontmatter_raises(self) -> None:
        write_source_guideline(self.source_root, "bare", "# No frontmatter\n")
        with self.assertRaises(mod.InstallerError):
            mod.guideline_skill_content(self.source_root, "bare")

    def test_missing_description_raises(self) -> None:
        write_source_guideline(
            self.source_root, "nodesc", "---\n---\n\n# No description\n"
        )
        with self.assertRaises(mod.InstallerError):
            mod.guideline_skill_content(self.source_root, "nodesc")

    def test_unclosed_frontmatter_raises(self) -> None:
        write_source_guideline(
            self.source_root, "unclosed", "---\ndescription: x\n"
        )
        with self.assertRaises(mod.InstallerError):
            mod.guideline_skill_content(self.source_root, "unclosed")

    def test_copy_pair_targets_skill_package(self) -> None:
        pairs = mod.guideline_copy_pairs(
            self.source_root, Path("/target"), "sample"
        )
        self.assertEqual(len(pairs), 1)
        src, dest = pairs[0]
        self.assertEqual(src, self.source_root / "guidelines" / "sample.md")
        self.assertEqual(
            dest, Path("/target/.agents/skills/guidelines-sample/SKILL.md")
        )

    def test_remove_paths_target_skill_package(self) -> None:
        paths = mod.guideline_remove_paths(Path("/target"), "sample")
        self.assertEqual(
            paths, [Path("/target/.agents/skills/guidelines-sample")]
        )


class GuidelineInstallTests(unittest.TestCase):
    """Install/uninstall lifecycle for guideline skill packages."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.source_root = Path(self._tmp.name) / "source"
        self.target = Path(self._tmp.name) / "target"
        self.source_root.mkdir()
        self.target.mkdir()
        write_source_guideline(self.source_root, "sample", GUIDELINE_SOURCE)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _install(self, *, override: bool = False):
        return mod.install_items(
            source_root=self.source_root,
            target_root=self.target,
            skills=[],
            agents=[],
            commands=[],
            scripts=[],
            guidelines=["sample"],
            override=override,
        )

    def test_install_writes_skill_package(self) -> None:
        result = self._install()
        self.assertTrue(result.ok, result.errors)
        skill_md = self.target / ".agents" / "skills" / "guidelines-sample" / "SKILL.md"
        self.assertTrue(skill_md.is_file())
        content = skill_md.read_text(encoding="utf-8")
        self.assertIn("name: guidelines-sample", content)
        self.assertEqual(
            result.installed, [".agents/skills/guidelines-sample/SKILL.md"]
        )

    def test_install_without_override_skips_existing(self) -> None:
        self._install()
        result = self._install(override=False)
        self.assertTrue(result.ok, result.errors)
        self.assertEqual(
            result.skipped, [".agents/skills/guidelines-sample/SKILL.md"]
        )

    def test_install_with_override_replaces(self) -> None:
        self._install()
        result = self._install(override=True)
        self.assertTrue(result.ok, result.errors)
        self.assertEqual(result.installed, [".agents/skills/guidelines-sample/SKILL.md"])

    def test_missing_source_reports_error(self) -> None:
        result = mod.install_items(
            source_root=self.source_root,
            target_root=self.target,
            skills=[],
            agents=[],
            commands=[],
            scripts=[],
            guidelines=["no-such-guideline"],
            override=False,
        )
        self.assertFalse(result.ok)
        self.assertTrue(
            any("no-such-guideline" in msg for msg in result.errors), result.errors
        )
        # An invalid name must not leave a partial directory behind.
        self.assertFalse(
            (self.target / ".agents" / "skills" / "guidelines-no-such-guideline").exists()
        )

    def test_uninstall_removes_installer_written_package(self) -> None:
        self._install()
        original_root = mod.REPO_ROOT
        mod.REPO_ROOT = self.source_root
        try:
            result = mod.uninstall_items(
                target_root=self.target,
                skills=[],
                agents=[],
                commands=[],
                scripts=[],
                guidelines=["sample"],
            )
        finally:
            mod.REPO_ROOT = original_root
        self.assertTrue(result.ok, result.errors)
        self.assertFalse(
            (self.target / ".agents" / "skills" / "guidelines-sample").exists()
        )
        self.assertIn(".agents/skills/guidelines-sample", result.removed)

    def test_uninstall_skips_user_modified_package(self) -> None:
        self._install()
        skill_md = self.target / ".agents" / "skills" / "guidelines-sample" / "SKILL.md"
        skill_md.write_text("---\nname: edited\n---\n\nEdited body.\n", encoding="utf-8")
        original_root = mod.REPO_ROOT
        mod.REPO_ROOT = self.source_root
        try:
            result = mod.uninstall_items(
                target_root=self.target,
                skills=[],
                agents=[],
                commands=[],
                scripts=[],
                guidelines=["sample"],
            )
        finally:
            mod.REPO_ROOT = original_root
        self.assertTrue(result.ok, result.errors)
        self.assertTrue(
            skill_md.is_file(), "a user-modified package must be kept"
        )
        self.assertIn(".agents/skills/guidelines-sample", result.skipped)

    def test_uninstall_after_source_edit_skips_stale_package(self) -> None:
        self._install()
        # Edit the source after install: the installed copy is now stale and
        # must read as user-modified (kept) on uninstall.
        write_source_guideline(
            self.source_root,
            "sample",
            GUIDELINE_SOURCE.replace("Sample", "Changed"),
        )
        original_root = mod.REPO_ROOT
        mod.REPO_ROOT = self.source_root
        try:
            result = mod.uninstall_items(
                target_root=self.target,
                skills=[],
                agents=[],
                commands=[],
                scripts=[],
                guidelines=["sample"],
            )
        finally:
            mod.REPO_ROOT = original_root
        self.assertTrue(result.ok, result.errors)
        self.assertTrue(
            (self.target / ".agents" / "skills" / "guidelines-sample" / "SKILL.md").is_file(),
            "a stale (source-edited) package must be kept on uninstall",
        )


class RealRepoGuidelineInstallTests(unittest.TestCase):
    """Install from the REAL repo: proves the shipped sources transform cleanly."""

    def test_real_repo_guidelines_install_and_uninstall(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            result = mod.install_items(
                source_root=REPO_ROOT,
                target_root=target,
                skills=[],
                agents=[],
                commands=[],
                scripts=[],
                guidelines=list(mod.INSTALLABLE_GUIDELINES),
                override=False,
            )
            self.assertTrue(result.ok, result.errors)
            for name in mod.INSTALLABLE_GUIDELINES:
                skill_md = (
                    target / ".agents" / "skills" / f"guidelines-{name}" / "SKILL.md"
                )
                self.assertTrue(skill_md.is_file(), f"{skill_md} must install")
                content = skill_md.read_text(encoding="utf-8")
                self.assertIn(f"name: guidelines-{name}", content)
                self.assertIn("description:", content)


class GuidelineDiscoveryTests(unittest.TestCase):
    """Guidelines stay explicit-only: never in the default selection or bundles."""

    def test_discover_guidelines_allowlist(self) -> None:
        discovered = mod.discover_guidelines()
        self.assertEqual(discovered, sorted(mod.INSTALLABLE_GUIDELINES))

    def test_default_selection_excludes_guideline_skills(self) -> None:
        # Simulate a repo carrying installed guideline skill packages: the
        # no-selector default must not pick them up as ordinary skills.
        with mock.patch.object(
            mod, "discover_skills", return_value=["cpp-coding", "guidelines-response"]
        ):
            selection = mod.resolve_cli_selection(
                bundle_ids=None,
                skill_names=None,
                agent_names=None,
                command_names=None,
                script_names=None,
                guideline_names=None,
                target_root=None,
            )
        self.assertIn("cpp-coding", selection.skills)
        self.assertNotIn("guidelines-response", selection.skills)

    def test_target_bundle_excludes_guideline_skills(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / ".agents" / "skills"
            (target / "guidelines-response").mkdir(parents=True)
            (target / "guidelines-response" / "SKILL.md").write_text(
                "---\nname: guidelines-response\n---\nbody\n", encoding="utf-8"
            )
            (target / "cpp-coding").mkdir()
            (target / "cpp-coding" / "SKILL.md").write_text(
                "---\nname: cpp-coding\n---\nbody\n", encoding="utf-8"
            )
            with mock.patch.object(
                mod,
                "discover_skills",
                return_value=["cpp-coding", "guidelines-response"],
            ):
                bundle = mod.build_target_bundle(Path(tmp))
        self.assertIn("cpp-coding", bundle.skills)
        self.assertNotIn("guidelines-response", bundle.skills)


if __name__ == "__main__":
    unittest.main()


class GuiGuidelinesPanelTests(unittest.TestCase):
    """The GUI exposes a Guidelines panel that installs skill packages."""

    def test_gui_panel_construction(self) -> None:
        import tkinter as tk

        with tempfile.TemporaryDirectory() as tmp:
            root_path = Path(tmp)
            write_source_guideline(root_path, "coding-behavior", GUIDELINE_SOURCE)
            original_root = mod.REPO_ROOT
            mod.REPO_ROOT = root_path
            try:
                root = tk.Tk()
                root.withdraw()
                app = mod.InstallerApp(root)
                try:
                    self.assertIn("coding-behavior", app.guideline_vars)
                finally:
                    root.destroy()
            finally:
                mod.REPO_ROOT = original_root

    def test_gui_run_installs_guideline_skill(self) -> None:
        import tkinter as tk

        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            target = Path(tmp) / "target"
            write_source_guideline(source, "coding-behavior", GUIDELINE_SOURCE)
            target.mkdir(parents=True, exist_ok=True)
            original_root = mod.REPO_ROOT
            mod.REPO_ROOT = source
            root = None
            try:
                root = tk.Tk()
                root.withdraw()
                app = mod.InstallerApp(root)
                app.target_var.set(str(target))
                app.guideline_vars["coding-behavior"].set(True)
                with mock.patch.object(
                    mod.messagebox, "showerror"
                ):
                    app._run()
                try:
                    skill_md = (
                        target
                        / ".agents"
                        / "skills"
                        / "guidelines-coding-behavior"
                        / "SKILL.md"
                    )
                    self.assertTrue(
                        skill_md.is_file(),
                        "the GUI run must install the guideline skill package",
                    )
                    self.assertIn(
                        "name: guidelines-coding-behavior",
                        skill_md.read_text(encoding="utf-8"),
                    )
                finally:
                    root.destroy()
            finally:
                mod.REPO_ROOT = original_root
                if root is not None:
                    try:
                        root.destroy()
                    except tk.TclError:
                        pass


class LocalGuidelinePackageTests(unittest.TestCase):
    """A local .agents/skills/guidelines-<name>/ install must not drift.

    The packages are generated and untracked (AGENTS.md cites the tracked
    guidelines/ sources), so this guard applies only when the checkout
    carries a local install; it skips on a fresh clone before installation.
    """

    def test_local_packages_match_regenerated_content(self) -> None:
        for name in mod.INSTALLABLE_GUIDELINES:
            skill_md = REPO_ROOT / ".agents" / "skills" / f"guidelines-{name}" / "SKILL.md"
            if not skill_md.is_file():
                self.skipTest("no local guideline install in this checkout")
            expected = mod.guideline_skill_content(REPO_ROOT, name)
            actual = skill_md.read_text(encoding="utf-8")
            self.assertEqual(
                actual,
                expected,
                f"{skill_md} drifted from guidelines/{name}.md — regenerate "
                "the guideline skill packages",
            )


class GuidelineLegacyResidueTests(unittest.TestCase):
    """--purge-legacy clears the pre-skill-layout .agents/guidelines/ dir."""

    def test_agents_guidelines_dir_in_purge_list(self) -> None:
        self.assertIn(".agents/guidelines", mod.LEGACY_PURGE_REL_PATHS)

    def test_purge_removes_legacy_guideline_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            legacy = target / ".agents" / "guidelines"
            legacy.mkdir(parents=True)
            (legacy / "response-guidelines.md").write_text(
                "---\ndescription: old\n---\nold body\n", encoding="utf-8"
            )
            result = mod.purge_legacy_paths(target)
            self.assertTrue(result.ok, result.errors)
            self.assertFalse(legacy.exists())
            self.assertIn(".agents/guidelines", result.removed)


class GuidelineUninstallGuardTests(unittest.TestCase):
    """--uninstall --skills must not bypass the guideline provenance rule."""

    def test_skills_uninstall_refuses_guideline_package(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            mod.install_items(
                source_root=REPO_ROOT,
                target_root=target,
                skills=[],
                agents=[],
                commands=[],
                scripts=[],
                guidelines=["response"],
                override=False,
            )
            original_root = mod.REPO_ROOT
            mod.REPO_ROOT = REPO_ROOT
            try:
                result = mod.uninstall_items(
                    target_root=target,
                    skills=["guidelines-response"],
                    agents=[],
                    commands=[],
                    scripts=[],
                    guidelines=[],
                )
            finally:
                mod.REPO_ROOT = original_root
            self.assertTrue(
                (target / ".agents" / "skills" / "guidelines-response").exists(),
                "--skills uninstall must not remove a guideline package",
            )
            self.assertTrue(
                any("guidelines-response" in msg for msg in result.errors),
                result.errors,
            )
