#!/usr/bin/env python3
"""Tests for install_portable_skill.py single-root .agents/ install behavior."""

from __future__ import annotations

import importlib.util
import os
import stat
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
_SIBLING_MODULES = (
    "quick_validate",
    "install_portable_skill",
    "scaffold_skill",
    "package_skill",
)


def _load_skill_modules():
    stashed = {
        mod_name: sys.modules.pop(mod_name)
        for mod_name in _SIBLING_MODULES
        if mod_name in sys.modules
    }
    old_path = list(sys.path)
    try:
        sys.path.insert(0, str(SCRIPTS_DIR))

        def _load(name: str, path: Path):
            spec = importlib.util.spec_from_file_location(name, path)
            if spec is None or spec.loader is None:
                raise RuntimeError(f"Could not load module from {path}")
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            spec.loader.exec_module(module)
            return module

        return (
            _load("install_portable_skill_test", SCRIPTS_DIR / "install_portable_skill.py"),
            _load("scaffold_skill_test", SCRIPTS_DIR / "scaffold_skill.py"),
            _load("package_skill_test", SCRIPTS_DIR / "package_skill.py"),
        )
    finally:
        sys.path[:] = old_path
        for mod_name in _SIBLING_MODULES:
            sys.modules.pop(mod_name, None)
        sys.modules.update(stashed)


install_mod, scaffold_mod, package_mod = _load_skill_modules()

install_portable_skill = install_mod.install_portable_skill
parse_args = install_mod.parse_args
scaffold_portable_skill = scaffold_mod.scaffold_portable_skill
SkillScaffoldError = install_mod.SkillScaffoldError

SKILL_NAME = "test-skill"
SKILL_DESCRIPTION = "Test skill for unit tests."
DEV_WORKFLOW_SKILL = "dev-workflow-orchestrator"


def shared_skill_md() -> str:
    return f"""---
name: {SKILL_NAME}
description: {SKILL_DESCRIPTION}
---

# Test Skill

Resolve `<SKILL_ROOT>` as the directory containing **this** skill's `SKILL.md`.

Shared skill body for tests.
"""


def write_bootstrap(source: Path) -> None:
    source.mkdir(parents=True, exist_ok=True)
    (source / "SKILL.md").write_text(shared_skill_md(), encoding="utf-8")


class InstallPortableSkillTests(unittest.TestCase):
    def test_dev_workflow_bootstrap_uses_installed_scripts_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = SCRIPTS_DIR.parents[2] / "skills" / DEV_WORKFLOW_SKILL

            install_portable_skill(
                root,
                source,
                DEV_WORKFLOW_SKILL,
                overwrite=True,
            )

            installed_skill = root / ".agents" / "skills" / DEV_WORKFLOW_SKILL / "SKILL.md"
            content = installed_skill.read_text(encoding="utf-8")
            self.assertIn("python .agents/skills/dev-workflow-orchestrator/scripts/record_baseline.py", content)
            self.assertNotIn("python tools/dev-workflow/", content)

    def test_rejects_category_subfolder_source(self) -> None:
        # t-004: a bootstrap source nested in a category folder (parent not
        # named "skills") is rejected at install time, matching the
        # validator's flat-root rule.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "skills" / "category" / SKILL_NAME
            write_bootstrap(source)

            with self.assertRaises(SkillScaffoldError) as ctx:
                install_portable_skill(
                    root,
                    source,
                    SKILL_NAME,
                    overwrite=True,
                )

            self.assertIn("direct child of a skills root", str(ctx.exception))
            # Fail-fast: nothing written on rejection.
            self.assertFalse((root / ".agents").exists())

    def test_install_writes_agents_root_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "skills" / SKILL_NAME
            write_bootstrap(source)

            written = install_portable_skill(
                root,
                source,
                SKILL_NAME,
                overwrite=True,
            )

            installed = root / ".agents" / "skills" / SKILL_NAME
            self.assertEqual(len(written), 1)
            self.assertEqual(written[0], installed.resolve())
            self.assertTrue((installed / "SKILL.md").is_file())

            self.assertFalse((root / ".ai").exists())
            self.assertFalse((root / ".cursor").exists())
            self.assertFalse((root / ".github").exists())

            # The only entry under .claude is the bridge symlink: there is no
            # real .claude/skills directory and no real .claude/skills/<name>.
            claude_skills = root / ".claude" / "skills"
            real_entries = [
                entry.name
                for entry in os.scandir(root / ".claude")
                if not entry.is_symlink()
            ]
            self.assertEqual(real_entries, [])
            self.assertTrue(claude_skills.is_symlink())
            self.assertFalse(stat.S_ISDIR(claude_skills.lstat().st_mode))

    def test_install_creates_bridge_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "skills" / SKILL_NAME
            write_bootstrap(source)

            install_portable_skill(
                root,
                source,
                SKILL_NAME,
                overwrite=True,
            )

            bridge = root / ".claude" / "skills"
            self.assertTrue(bridge.is_symlink())
            self.assertEqual(os.readlink(bridge), "../.agents/skills")
            self.assertEqual(
                bridge.resolve(),
                (root / ".agents" / "skills").resolve(),
            )
            # Claude Code can see the installed skill through the bridge.
            self.assertTrue((bridge / SKILL_NAME / "SKILL.md").is_file())

    def test_install_bridge_conflict_errors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            legacy = root / ".claude" / "skills"
            legacy.mkdir(parents=True)
            (legacy / "stale-skill").mkdir()
            source = root / "skills" / SKILL_NAME
            write_bootstrap(source)

            with self.assertRaises(SkillScaffoldError) as ctx:
                install_portable_skill(
                    root,
                    source,
                    SKILL_NAME,
                    overwrite=True,
                )

            self.assertIn("purge", str(ctx.exception).lower())
            # The real directory must not be clobbered.
            self.assertTrue(legacy.is_dir())
            self.assertFalse(legacy.is_symlink())
            self.assertTrue((legacy / "stale-skill").is_dir())

    def test_install_over_command_skill_refused(self) -> None:
        """cr-004: installing a plain skill over a command-skill is refused.

        The skill installer must never silently convert a slash-command into a
        model-invocable skill (the copy would drop disable-model-invocation:
        true) — refused even with overwrite=True, before any write, and the
        existing command-skill is left untouched.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "skills" / SKILL_NAME
            write_bootstrap(source)
            command_skill_dir = root / ".agents" / "skills" / SKILL_NAME
            command_skill_dir.mkdir(parents=True)
            existing = command_skill_dir / "SKILL.md"
            existing.write_text(
                "---\n"
                f"name: {SKILL_NAME}\n"
                f"description: {SKILL_DESCRIPTION}\n"
                "disable-model-invocation: true\n"
                "---\n\n"
                f"# {SKILL_NAME}\n",
                encoding="utf-8",
            )
            original = existing.read_text(encoding="utf-8")

            with self.assertRaises(SkillScaffoldError) as ctx:
                install_portable_skill(
                    root,
                    source,
                    SKILL_NAME,
                    overwrite=True,
                )

            self.assertIn("command", str(ctx.exception).lower())
            # Destination untouched: the command-skill flag survives.
            self.assertEqual(existing.read_text(encoding="utf-8"), original)
            self.assertIn("disable-model-invocation: true", original)

    def test_install_over_undecodable_dest_skill_md_no_traceback(self) -> None:
        """cr-102: a dest SKILL.md with non-UTF-8 bytes must not traceback.

        is_command_skill reads the dest SKILL.md to run the cr-004 guard; an
        undecodable file used to raise UnicodeDecodeError out of main() as a
        raw traceback. Unreadable reads as not-a-command-skill (the tools
        twin's semantics), so the guard passes and the install proceeds as a
        plain overwrite.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "skills" / SKILL_NAME
            write_bootstrap(source)
            dest_dir = root / ".agents" / "skills" / SKILL_NAME
            dest_dir.mkdir(parents=True)
            (dest_dir / "SKILL.md").write_bytes(b"\x80\xff")

            written = install_portable_skill(
                root,
                source,
                SKILL_NAME,
                overwrite=True,
            )

            self.assertEqual(len(written), 1)
            installed = dest_dir / "SKILL.md"
            self.assertTrue(installed.is_file())
            self.assertEqual(
                installed.read_text(encoding="utf-8"),
                shared_skill_md(),
            )

    def test_install_bridge_wrong_target_symlink_warns_and_keeps(self) -> None:
        """cr-011a: a bridge symlink pointing elsewhere is left as-is.

        The install must not clobber a user-managed .claude/skills symlink;
        the bridge function reports the mismatch (warn + return False) and
        the skill install itself still succeeds.
        """
        import contextlib
        import io

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            other = root / "elsewhere"
            other.mkdir()
            (root / ".claude").mkdir()
            os.symlink("elsewhere", root / ".claude" / "skills")
            source = root / "skills" / SKILL_NAME
            write_bootstrap(source)

            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                written = install_portable_skill(
                    root,
                    source,
                    SKILL_NAME,
                    overwrite=True,
                )

            self.assertEqual(len(written), 1)
            bridge = root / ".claude" / "skills"
            self.assertTrue(bridge.is_symlink())
            self.assertEqual(os.readlink(bridge), "elsewhere")
            self.assertIn("expected", err.getvalue())

    def test_install_bridge_is_idempotent(self) -> None:
        """cr-011b: a second install reuses the existing bridge symlink."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "skills" / SKILL_NAME
            write_bootstrap(source)

            install_portable_skill(root, source, SKILL_NAME, overwrite=True)
            bridge = root / ".claude" / "skills"
            self.assertTrue(bridge.is_symlink())
            self.assertEqual(os.readlink(bridge), "../.agents/skills")

            install_portable_skill(root, source, SKILL_NAME, overwrite=True)

            self.assertTrue(bridge.is_symlink())
            self.assertEqual(os.readlink(bridge), "../.agents/skills")

    def test_install_claude_file_at_bridge_parent_warns(self) -> None:
        """cr-007: a regular file at <root>/.claude must not traceback.

        The mkdir inside ensure_bridge_symlink raises FileExistsError, which
        main() does not catch — the bridge failure is reported as a warning
        and the install proceeds without the bridge (nothing written under
        .claude/, the skill itself still installs).
        """
        import contextlib
        import io

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".claude").write_text("not a directory", encoding="utf-8")
            source = root / "skills" / SKILL_NAME
            write_bootstrap(source)

            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                written = install_portable_skill(
                    root,
                    source,
                    SKILL_NAME,
                    overwrite=True,
                )

            self.assertEqual(len(written), 1)
            # The regular file is untouched; no bridge was created.
            claude = root / ".claude"
            self.assertTrue(claude.is_file())
            self.assertFalse(claude.is_symlink())
            self.assertIn("warning", err.getvalue())

    def test_cli_drops_note_args(self) -> None:
        base_args = ["--root", "root", "--name", SKILL_NAME, "--source", "source"]
        for note_arg in ("--claude-note", "--cursor-note", "--github-note"):
            with self.assertRaises(SystemExit) as ctx:
                parse_args(base_args + [note_arg, "extra note"])
            self.assertEqual(ctx.exception.code, 2)

    def test_scaffold_targets_agents_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            written = scaffold_portable_skill(root, SKILL_NAME, overwrite=True)

            skill_dir = root / ".agents" / "skills" / SKILL_NAME
            self.assertEqual(written, [skill_dir.resolve()])
            self.assertTrue((skill_dir / "SKILL.md").is_file())
            self.assertFalse((root / ".ai").exists())
            self.assertFalse((root / ".cursor").exists())
            self.assertFalse((root / ".claude").exists())

    def test_install_and_package_exclude_non_runtime_files(self) -> None:
        from unittest import mock
        import zipfile

        self.assertEqual(package_mod.EXCLUDE_DIRS, set(install_mod.IGNORE_DIR_NAMES))
        self.assertEqual(package_mod.EXCLUDE_GLOBS, set(install_mod.IGNORE_FILE_GLOBS))
        self.assertTrue(package_mod.should_exclude(Path(f"{SKILL_NAME}/scripts/helper_test.py")))
        self.assertTrue(package_mod.should_exclude(Path(f"{SKILL_NAME}/conftest.py")))
        self.assertTrue(package_mod.should_exclude(Path(f"{SKILL_NAME}/.DS_Store")))
        self.assertTrue(package_mod.should_exclude(Path(f"{SKILL_NAME}/node_modules/pkg/index.js")))
        self.assertFalse(package_mod.should_exclude(Path(f"{SKILL_NAME}/SKILL.md")))

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "skills" / SKILL_NAME
            write_bootstrap(source)
            (source / "eval-queries.json").write_text("[]", encoding="utf-8")
            (source / "SOURCES.md").write_text("# Sources\n", encoding="utf-8")
            (source / ".DS_Store").write_text("ds", encoding="utf-8")
            (source / ".coverage").write_text("cov", encoding="utf-8")
            (source / ".coverage.worker1").write_text("cov", encoding="utf-8")
            (source / "stale.skill").write_text("zip", encoding="utf-8")
            (source / "evals").mkdir()
            (source / "evals" / "evals.json").write_text("{}", encoding="utf-8")
            (source / ".pytest_cache").mkdir()
            (source / ".pytest_cache" / "CACHEDIR.TAG").write_text("t", encoding="utf-8")
            (source / ".hypothesis").mkdir()
            (source / ".hypothesis" / "examples").write_text("h", encoding="utf-8")
            (source / "node_modules" / "pkg").mkdir(parents=True)
            (source / "node_modules" / "pkg" / "index.js").write_text("0", encoding="utf-8")
            scripts = source / "scripts"
            scripts.mkdir()
            (scripts / "helper.py").write_text("x = 1\n", encoding="utf-8")
            (scripts / "test_helper.py").write_text("def test_x(): pass\n", encoding="utf-8")
            (scripts / "helper_test.py").write_text("def test_y(): pass\n", encoding="utf-8")
            (scripts / "conftest.py").write_text("pass\n", encoding="utf-8")
            (scripts / ".ruff_cache").mkdir()
            (scripts / ".ruff_cache" / "CACHEDIR.TAG").write_text("t", encoding="utf-8")
            (scripts / "testdata").mkdir()
            (scripts / "testdata" / "fixture.json").write_text("{}", encoding="utf-8")
            (scripts / "fixtures").mkdir()
            (scripts / "fixtures" / "sample.ui").write_text("<ui/>", encoding="utf-8")

            install_portable_skill(root, source, SKILL_NAME, overwrite=True)
            installed = root / ".agents" / "skills" / SKILL_NAME
            self.assertTrue((installed / "SKILL.md").is_file())
            self.assertTrue((installed / "scripts" / "helper.py").is_file())
            for rel in (
                "eval-queries.json",
                "SOURCES.md",
                ".DS_Store",
                ".coverage",
                ".coverage.worker1",
                "stale.skill",
                "evals",
                ".pytest_cache",
                ".hypothesis",
                "node_modules",
                "scripts/test_helper.py",
                "scripts/helper_test.py",
                "scripts/conftest.py",
                "scripts/.ruff_cache",
                "scripts/testdata",
                "scripts/fixtures",
            ):
                self.assertFalse((installed / rel).exists(), f"{rel} should not install")

            walked_dirs: list[Path] = []
            real_walk = package_mod.os.walk

            def tracking_walk(top, *args, **kwargs):
                for dirpath, dirnames, filenames in real_walk(top, *args, **kwargs):
                    walked_dirs.append(Path(dirpath))
                    yield dirpath, dirnames, filenames

            with mock.patch.object(package_mod.os, "walk", side_effect=tracking_walk):
                archive = package_mod.package_skill(source, root / "dist")
            self.assertIsNotNone(archive)

            walked_parts = {
                part
                for walked in walked_dirs
                for part in walked.relative_to(source).parts
            }
            for pruned_dir in ("node_modules", ".pytest_cache", ".hypothesis", "evals", ".ruff_cache", "testdata", "fixtures"):
                self.assertNotIn(pruned_dir, walked_parts, f"os.walk descended into {pruned_dir}")

            with zipfile.ZipFile(archive) as zf:
                names = set(zf.namelist())
            self.assertIn(f"{SKILL_NAME}/SKILL.md", names)
            self.assertIn(f"{SKILL_NAME}/scripts/helper.py", names)
            for banned in (
                "eval-queries.json",
                "SOURCES.md",
                ".DS_Store",
                ".coverage",
                ".coverage.worker1",
                "stale.skill",
                "test_helper.py",
                "helper_test.py",
                "conftest.py",
                "index.js",
                "examples",
                "CACHEDIR.TAG",
                "fixture.json",
                "sample.ui",
            ):
                self.assertFalse(any(n.endswith(banned) for n in names), f"{banned} leaked into .skill")


if __name__ == "__main__":
    unittest.main()
