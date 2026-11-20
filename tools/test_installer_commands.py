#!/usr/bin/env python3
"""Tests for command install/uninstall in installer.py.

Commands are command-skills: skills under .agents/skills/cmd-<name>/ whose
SKILL.md carries `disable-model-invocation: true` (the slash command stays
/<name>). They share the .agents/skills/ namespace with plain skills and
install as a directory tree, not tool files.
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import os
import sys
import tempfile
import unittest
import unittest.mock
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


REPO_ROOT = TOOLS_DIR.parent

GIT_COMMIT_DESCRIPTION = (
    "Draft a Conventional Commit message for staged changes with "
    "commit-message-writer, then commit those staged changes without pushing."
)

def write_plain_skill(root: Path, name: str) -> Path:
    """Write a plain (non-command) skill under <root>/.agents/skills/<name>/."""
    skill_dir = root / ".agents" / "skills" / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text(
        f"---\nname: {name}\ndescription: plain skill\n---\n\n# {name}\n",
        encoding="utf-8",
    )
    return skill_md

def write_command_skill(
    root: Path,
    name: str,
    *,
    disable_model_invocation: bool = True,
    description: str | None = None,
) -> Path:
    """Write a command-skill under <root>/.agents/skills/cmd-<name>/SKILL.md."""
    skill_dir = root / ".agents" / "skills" / f"cmd-{name}"
    skill_dir.mkdir(parents=True, exist_ok=True)
    if description is None:
        description = (
            GIT_COMMIT_DESCRIPTION
            if disable_model_invocation
            else "plain skill"
        )
    flag = "disable-model-invocation: true\n" if disable_model_invocation else ""
    frontmatter = (
        "---\n"
        f"name: {name}\n"
        f"description: {description}\n"
        f"{flag}"
        "---\n"
    )
    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text(f"{frontmatter}\n# {name}\n", encoding="utf-8")
    return skill_md

class CommandDiscoveryTests(unittest.TestCase):
    def test_discover_commands_includes_flag_command_skill(self) -> None:
        """The commit command is discovered via its invocation flag."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_command_skill(root, "commit")
            original_root = mod.REPO_ROOT
            mod.REPO_ROOT = root
            try:
                commands = mod.discover_commands()
            finally:
                mod.REPO_ROOT = original_root

            self.assertIn("commit", commands)

    def test_discover_commands_excludes_plain_skills(self) -> None:
        """Commands are command-skills: only flag-bearing skills are commands."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_command_skill(root, "demo-command")
            write_command_skill(
                root, "plain-skill", disable_model_invocation=False
            )
            original_root = mod.REPO_ROOT
            mod.REPO_ROOT = root
            try:
                commands = mod.discover_commands()
            finally:
                mod.REPO_ROOT = original_root

            self.assertIn("demo-command", commands)
            self.assertNotIn("plain-skill", commands)

    def test_load_command_descriptions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_command_skill(root, "commit")
            original_root = mod.REPO_ROOT
            mod.REPO_ROOT = root
            try:
                descriptions = mod.load_command_descriptions(["commit"])
            finally:
                mod.REPO_ROOT = original_root

            self.assertIn("commit", descriptions)
            self.assertIn("commit-message-writer", descriptions["commit"])

    def test_discover_commands_in_project_filters_by_flag(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_command_skill(root, "demo-command")
            write_command_skill(
                root, "plain-skill", disable_model_invocation=False
            )
            self.assertEqual(
                mod.discover_commands_in_project(root), ["demo-command"]
            )

class CommandInstallTests(unittest.TestCase):
    def test_install_command_copies_skill_tree(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            target = Path(tmp) / "target"
            write_command_skill(source, "demo-command")

            result = mod.install_items(
                source_root=source,
                target_root=target,
                skills=[],
                agents=[],
                commands=["demo-command"],
                override=False,
            )

            self.assertTrue(result.ok, result.errors)
            installed = target / ".agents" / "skills" / "cmd-demo-command" / "SKILL.md"
            self.assertTrue(installed.is_file())
            content = installed.read_text(encoding="utf-8")
            self.assertIn("disable-model-invocation: true", content)
            self.assertIn(".agents/skills/cmd-demo-command", result.installed[0])

    def test_install_skill_never_touches_command_skill_install(self) -> None:
        """cr-004 (structural, cmd- dir prefix): a plain skill and a
        command-skill of the same name install to different directories
        (.agents/skills/<name>/ vs .agents/skills/cmd-<name>/), so a skill
        install can no longer clobber or flip a command-skill install.
        """
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            target = Path(tmp) / "target"
            write_plain_skill(source, "demo-command")
            existing = write_command_skill(target, "demo-command")
            original = existing.read_text(encoding="utf-8")

            result = mod.install_items(
                source_root=source,
                target_root=target,
                skills=["demo-command"],
                agents=[],
                commands=[],
                override=True,
            )

            self.assertTrue(result.ok, result.errors)
            # Command-skill install untouched, flag intact.
            self.assertEqual(existing.read_text(encoding="utf-8"), original)
            self.assertIn("disable-model-invocation: true", original)
            # Plain skill installed at its own, unprefixed directory.
            self.assertTrue(
                (target / ".agents" / "skills" / "demo-command" / "SKILL.md").is_file()
            )

    def test_uninstall_skills_leaves_command_skill_alone(self) -> None:
        """cr-004 (structural, cmd- dir prefix): --uninstall --skills cannot
        reach the command-skill install at .agents/skills/cmd-<name>/; the
        command selector (--uninstall --commands) remains the removal path.
        """
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            existing = write_command_skill(target, "demo-command")

            result = mod.uninstall_items(
                target_root=target,
                skills=["demo-command"],
                agents=[],
                commands=[],
            )

            self.assertTrue(result.ok, result.errors)
            self.assertTrue(existing.is_file(), "command-skill must survive a skills-only uninstall")
            self.assertIn("disable-model-invocation: true", existing.read_text(encoding="utf-8"))

    def test_uninstall_commands_still_removes_command_skill(self) -> None:
        """cr-004 guard is scoped to the skills pass: the command selector
        keeps removing command-skills (command_remove_paths unchanged)."""
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            write_command_skill(target, "demo-command")

            result = mod.uninstall_items(
                target_root=target,
                skills=[],
                agents=[],
                commands=["demo-command"],
            )

            self.assertTrue(result.ok, result.errors)
            self.assertFalse((target / ".agents" / "skills" / "cmd-demo-command").exists())

    def test_commands_selector_rejects_plain_skill(self) -> None:
        """cr-006: --commands errors when the cmd-<name> source lacks the
        invocation flag instead of installing a plain skill as a command.
        """
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            target = Path(tmp) / "target"
            # Plain skill planted in the command install dir — the only way
            # a flagless source can now reach the command pass.
            write_plain_skill(source, "cmd-plain-name")

            result = mod.install_items(
                source_root=source,
                target_root=target,
                skills=[],
                agents=[],
                commands=["plain-name"],
                override=False,
            )

            self.assertFalse(result.ok)
            self.assertTrue(
                any("not a command-skill" in msg for msg in result.errors),
                result.errors,
            )
            self.assertFalse((target / ".agents" / "skills" / "cmd-plain-name").exists())

    def test_command_refuses_to_replace_plain_skill_dest(self) -> None:
        """cr-105: --commands over an existing plain-skill dest is refused.

        The dest name carries a plain skill (no disable-model-invocation);
        installing a command-skill over it would rmtree user-authored files
        and flip the kind. Refused even under --override, matching the
        bootstrap command installer (scaffold_command.py) and mirroring the
        skills pass's cr-004 guard.
        """
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            target = Path(tmp) / "target"
            write_command_skill(source, "shared-name")
            # Dest: an existing plain skill with user-authored content,
            # squatting on the command install dir cmd-shared-name.
            dest_md = write_plain_skill(target, "cmd-shared-name")
            dest_md.write_text(
                "---\nname: shared-name\ndescription: user-authored\n---\n\n"
                "# User content\n\nDo not delete me.\n",
                encoding="utf-8",
            )

            result = mod.install_items(
                source_root=source,
                target_root=target,
                skills=[],
                agents=[],
                commands=["shared-name"],
                override=True,
            )

            self.assertFalse(result.ok)
            self.assertTrue(
                any(
                    "refusing to replace existing plain skill" in msg
                    for msg in result.errors
                ),
                result.errors,
            )
            dest_text = dest_md.read_text(encoding="utf-8")
            self.assertIn("Do not delete me.", dest_text)
            self.assertNotIn(
                "disable-model-invocation", dest_text,
                "the plain skill must not be converted to a command-skill",
            )
            self.assertNotIn(
                "refusing to replace existing plain skill",
                " ".join(result.installed),
            )

    def test_command_override_replaces_undecodable_stale_dest(self) -> None:
        """cr-105 parity with cr-102: an undecodable dest SKILL.md is stale
        content, not a skill — --override replaces it, no UnicodeDecodeError
        traceback (the read must degrade, never raise)."""
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            target = Path(tmp) / "target"
            write_command_skill(source, "broken-dest")
            dest_dir = target / ".agents" / "skills" / "cmd-broken-dest"
            dest_dir.mkdir(parents=True)
            (dest_dir / "SKILL.md").write_bytes(b"\x80\xff not utf-8")

            result = mod.install_items(
                source_root=source,
                target_root=target,
                skills=[],
                agents=[],
                commands=["broken-dest"],
                override=True,
            )

            self.assertTrue(result.ok, result.errors)
            self.assertIn(
                "disable-model-invocation: true",
                (dest_dir / "SKILL.md").read_text(encoding="utf-8"),
                "stale undecodable dest must be replaced under --override",
            )

    def test_install_command_skips_existing_without_override(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            target = Path(tmp) / "target"
            write_command_skill(source, "demo-command")
            stale = write_command_skill(target, "demo-command")
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
            self.assertIn(".agents/skills/cmd-demo-command", result.skipped)
            self.assertEqual(stale.read_text(encoding="utf-8"), "stale")

    def test_uninstall_command_removes_skill_tree(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            write_command_skill(target, "demo-command")

            result = mod.uninstall_items(
                target_root=target,
                skills=[],
                agents=[],
                commands=["demo-command"],
            )

            self.assertTrue(result.ok, result.errors)
            self.assertFalse((target / ".agents" / "skills" / "cmd-demo-command").exists())

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
            self.assertIn("skill, agent, command, scripts, or guideline", str(ctx.exception))

class BridgeCreationTests(unittest.TestCase):
    """fd-002/fd-003/fd-019 regression coverage for bridge + default uninstall."""

    def test_commands_only_install_creates_bridge(self) -> None:
        """fd-002: a commands-only install (no skills pass) still bridges.

        Command-skills install only into .agents/skills/; without this the
        commands loop's ensure_bridge_symlink call, Claude Code cannot
        discover them on a commands-only install.
        """
        import os

        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            target = Path(tmp) / "target"
            write_command_skill(source, "demo-command")

            result = mod.install_items(
                source_root=source,
                target_root=target,
                skills=[],
                agents=[],
                commands=["demo-command"],
                override=False,
            )

            self.assertTrue(result.ok, result.errors)
            bridge = target / ".claude" / "skills"
            self.assertTrue(bridge.is_symlink(), "commands-only install must bridge")
            self.assertEqual(os.readlink(bridge), "../.agents/skills")
            self.assertTrue(
                (bridge / "cmd-demo-command" / "SKILL.md").is_file(),
                "the command-skill must be reachable through the bridge",
            )

    def test_bridge_refusal_degrades_installs_not_abort(self) -> None:
        """fd-003: a real .claude/skills dir (legacy target) warns + continues.

        The wrapper catches the helper's refusal; a bulk install against a
        legacy target must not abort mid-run — both skills copy, the real
        dir is untouched, and a warning reaches stderr.
        """
        import contextlib
        import io

        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            target = Path(tmp) / "target"
            write_plain_skill(source, "skill-a")
            write_plain_skill(source, "skill-b")
            legacy = target / ".claude" / "skills"
            legacy.mkdir(parents=True)
            (legacy / "stale-skill").mkdir()
            marker = legacy / "stale-skill" / "SKILL.md"
            marker.write_text("---\nname: stale-skill\ndescription: old\n---\n", encoding="utf-8")

            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                result = mod.install_items(
                    source_root=source,
                    target_root=target,
                    skills=["skill-a", "skill-b"],
                    agents=[],
                    commands=[],
                    override=False,
                )

            self.assertTrue(
                result.ok,
                f"legacy real-dir bridge must degrade, not abort: {result.errors}",
            )
            self.assertIn(".agents/skills/skill-a", result.installed)
            self.assertIn(".agents/skills/skill-b", result.installed)
            self.assertTrue(marker.is_file(), "the real dir must not be clobbered")
            self.assertIn("warning", stderr.getvalue().lower())

    def test_uninstall_commands_removes_legacy_unprefixed_install(self) -> None:
        """F2 regression: --uninstall --commands also removes a pre-dir-prefix
        install (.agents/skills/<name> with the invocation flag) so the host
        stops exposing the stale slash command; a plain skill on the same
        name must survive (cr-004 semantics).
        """
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            legacy = write_command_skill(target, "old-style")
            # Plain skill with the same name must survive the legacy sweep.
            plain = write_plain_skill(target, "plain-style")

            result = mod.uninstall_items(
                target_root=target,
                skills=[],
                agents=[],
                commands=["old-style", "plain-style"],
            )

            self.assertTrue(result.ok, result.errors)
            self.assertFalse(legacy.exists(), "legacy unprefixed command-skill must be removed")
            self.assertTrue(plain.is_file(), "plain skill must survive the legacy sweep")

    def test_default_uninstall_of_command_skill_exits_zero(self) -> None:
        """fd-019: default no-selector uninstall dedupes like explicit paths.

        discover_skills() returns command-skill names too; without the
        default-branch dedupe the skills pass hits the cr-004 cross-kind
        guard for each command-skill and a clean teardown false-fails.
        """
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            target = Path(tmp) / "target"
            write_plain_skill(source, "plain-skill")
            write_command_skill(source, "demo-command")
            mod.install_items(
                source_root=source,
                target_root=target,
                skills=["plain-skill"],
                agents=[],
                commands=["demo-command"],
                override=False,
            )

            original_root = mod.REPO_ROOT
            mod.REPO_ROOT = source
            try:
                code = mod.run_cli([str(target), "--uninstall"])
            finally:
                mod.REPO_ROOT = original_root

            self.assertEqual(code, 0, "default uninstall of a clean target must exit 0")
            self.assertFalse((target / ".agents" / "skills" / "cmd-demo-command").exists())
            self.assertFalse((target / ".agents" / "skills" / "plain-skill").exists())

class PurgeLegacyTests(unittest.TestCase):
    """--purge-legacy: remove a target's pre-single-root install leftovers."""

    def _seed_legacy(self, target: Path) -> None:
        (target / ".ai" / "skills" / "old").mkdir(parents=True, exist_ok=True)
        (target / ".ai" / "skills" / "old" / "SKILL.md").write_text(
            "---\nname: old\ndescription: old\n---\n", encoding="utf-8"
        )
        (target / ".cursor" / "skills").mkdir(parents=True, exist_ok=True)
        (target / ".cursor" / "commands").mkdir(parents=True, exist_ok=True)
        (target / ".cursor" / "agents").mkdir(parents=True, exist_ok=True)
        (target / ".github" / "prompts").mkdir(parents=True, exist_ok=True)
        # cr-003: the old installer also wrote .github/skills/<name>/SKILL.md
        # (the removed TOOL_SKILL_DIRS layout) — a legacy Copilot wrapper dir.
        (target / ".github" / "skills" / "old").mkdir(parents=True, exist_ok=True)
        (target / ".claude" / "commands").mkdir(parents=True, exist_ok=True)

    def test_purge_legacy_removes_all_legacy_roots(self) -> None:
        """The purge removes .ai/ and the wrapper dirs, keeps current paths."""
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir(parents=True)
            self._seed_legacy(target)
            # Content the purge must NOT touch.
            agents_target = target / ".claude" / "agents" / "keep.md"
            agents_target.parent.mkdir(parents=True, exist_ok=True)
            agents_target.write_text("---\nname: keep\n---\n", encoding="utf-8")
            agents_github = target / ".github" / "agents" / "keep.agent.md"
            agents_github.parent.mkdir(parents=True, exist_ok=True)
            agents_github.write_text("---\nname: keep\n---\n", encoding="utf-8")

            result = mod.purge_legacy_paths(target)

            self.assertTrue(result.ok, result.errors)
            for rel in (
                ".ai",
                ".cursor/skills",
                ".cursor/commands",
                ".cursor/agents",
                ".github/prompts",
                ".github/skills",
                ".claude/commands",
            ):
                self.assertFalse(
                    (target / rel).exists(), f"{rel} must be removed"
                )
            # .claude/agents and .github/agents are current-layout paths.
            self.assertTrue(agents_target.is_file())
            self.assertTrue(agents_github.is_file())

    def test_purge_legacy_keeps_bridge_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir(parents=True)
            self._seed_legacy(target)
            # Replace the seeded real .claude/skills with the bridge symlink.
            bridge = target / ".claude" / "skills"
            os.symlink("../.agents/skills", bridge)

            result = mod.purge_legacy_paths(target)

            self.assertTrue(result.ok, result.errors)
            self.assertTrue(bridge.is_symlink())
            self.assertEqual(os.readlink(bridge), "../.agents/skills")
            self.assertNotIn(".claude/skills", result.removed)

    def test_purge_legacy_removes_real_claude_skills_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir(parents=True)
            (target / ".claude" / "skills" / "old").mkdir(parents=True)

            result = mod.purge_legacy_paths(target)

            self.assertTrue(result.ok, result.errors)
            self.assertFalse((target / ".claude" / "skills").exists())
            self.assertIn(".claude/skills", result.removed)

    def test_purge_legacy_leaves_agents_dir_untouched(self) -> None:
        """--agents composes with --purge-legacy but .claude/agents survives.

        .claude/agents/ is the CURRENT dual-target agent path (only
        .cursor/agents is legacy), so a purge must leave it intact even with
        an agent selector in play.
        """
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir(parents=True)
            self._seed_legacy(target)
            keep = target / ".claude" / "agents" / "keep.md"
            keep.parent.mkdir(parents=True, exist_ok=True)
            keep.write_text("---\nname: keep\n---\n", encoding="utf-8")

            result = mod.purge_legacy_paths(target)

            self.assertTrue(result.ok, result.errors)
            self.assertTrue(
                (target / ".claude" / "agents" / "keep.md").is_file()
            )
            self.assertFalse((target / ".cursor" / "agents").exists())

    def test_purge_legacy_requires_existing_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "missing"
            with self.assertRaises(mod.InstallerError):
                mod.purge_legacy_paths(missing)

    def test_purge_refuses_repo_root(self) -> None:
        """cr-001: --purge-legacy must never purge the AIConfig repo itself.

        The repo is its own plausible first target; purging it would rmtree
        the gitignored .ai/ workflow state (unrecoverable) plus the real
        .claude/skills/ and .claude/commands/. purge_legacy_paths must apply
        the same validate_target guard every mutating install path uses.
        """
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp) / "repo"
            self._seed_legacy(repo_root)

            original_root = mod.REPO_ROOT
            mod.REPO_ROOT = repo_root
            try:
                with self.assertRaises(mod.InstallerError) as ctx:
                    mod.purge_legacy_paths(repo_root)
            finally:
                mod.REPO_ROOT = original_root

            self.assertIn("AIConfig repository root", str(ctx.exception))
            # Nothing removed: every seeded legacy path survives.
            self.assertTrue((repo_root / ".ai" / "skills" / "old" / "SKILL.md").is_file())
            self.assertTrue((repo_root / ".cursor" / "skills").is_dir())
            self.assertTrue((repo_root / ".github" / "prompts").is_dir())
            self.assertTrue((repo_root / ".claude" / "commands").is_dir())

    def test_purge_refuses_target_inside_repo_root(self) -> None:
        """cr-001 subpath variant: a target inside REPO_ROOT is refused too."""
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp) / "repo"
            inner = repo_root / "subdir"
            self._seed_legacy(inner)

            original_root = mod.REPO_ROOT
            mod.REPO_ROOT = repo_root
            try:
                with self.assertRaises(mod.InstallerError) as ctx:
                    mod.purge_legacy_paths(inner)
            finally:
                mod.REPO_ROOT = original_root

            self.assertIn("inside the AIConfig repository", str(ctx.exception))
            self.assertTrue((inner / ".ai" / "skills" / "old" / "SKILL.md").is_file())

    def test_run_cli_reports_purge_when_selection_fails(self) -> None:
        """cr-009: a purge's irreversible report is never discarded.

        run_cli purges before resolving the selection; when the selection
        later raises InstallerError, the purge output must still be printed
        alongside the error (the purge already happened). An unknown bundle
        is the trigger: resolve_bundle raises InstallerError, so the CLI
        exits 2 after the purge report.
        """
        import contextlib
        import io

        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            target = Path(tmp) / "target"
            target.mkdir(parents=True)
            self._seed_legacy(target)

            original_root = mod.REPO_ROOT
            mod.REPO_ROOT = source
            try:
                captured_out = io.StringIO()
                captured_err = io.StringIO()
                with contextlib.redirect_stdout(captured_out):
                    with contextlib.redirect_stderr(captured_err):
                        code = mod.run_cli(
                            [
                                str(target),
                                "--purge-legacy",
                                "--bundles",
                                "no-such-bundle",
                            ]
                        )
            finally:
                mod.REPO_ROOT = original_root

            self.assertEqual(code, 2)
            self.assertIn("Purged legacy paths", captured_out.getvalue())
            self.assertIn("error:", captured_err.getvalue())
            # The purge really happened; the failing selection removed nothing.
            self.assertFalse((target / ".ai").exists())

    def test_run_cli_reports_purge_when_operation_records_errors(self) -> None:
        """cr-009 companion: the per-name-error exit path also keeps the
        purge report (the purge ran before the install errors surfaced)."""
        import contextlib
        import io

        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            target = Path(tmp) / "target"
            target.mkdir(parents=True)
            self._seed_legacy(target)

            original_root = mod.REPO_ROOT
            mod.REPO_ROOT = source
            try:
                captured_out = io.StringIO()
                with contextlib.redirect_stdout(captured_out):
                    code = mod.run_cli(
                        [
                            str(target),
                            "--purge-legacy",
                            "--skills",
                            "missing-skill",
                        ]
                    )
            finally:
                mod.REPO_ROOT = original_root

            self.assertEqual(code, 1)
            self.assertIn("Purged legacy paths", captured_out.getvalue())
            self.assertIn("Errors:", captured_out.getvalue())

    def test_run_cli_purge_legacy_standalone(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir(parents=True)
            self._seed_legacy(target)

            code = mod.run_cli([str(target), "--purge-legacy"])

            self.assertEqual(code, 0)
            self.assertFalse((target / ".ai").exists())
            self.assertFalse((target / ".cursor" / "skills").exists())
            self.assertFalse((target / ".github" / "prompts").exists())

    def test_run_cli_purge_legacy_standalone_installs_nothing(self) -> None:
        """Standalone --purge-legacy is purge-only: the no-selector default
        install must not kick in."""
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            target = Path(tmp) / "target"
            target.mkdir(parents=True)
            skill_dir = source / ".agents" / "skills" / "git-guide"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                "---\nname: git-guide\ndescription: Git\n---\n",
                encoding="utf-8",
            )
            self._seed_legacy(target)

            original_root = mod.REPO_ROOT
            mod.REPO_ROOT = source
            try:
                code = mod.run_cli([str(target), "--purge-legacy"])
            finally:
                mod.REPO_ROOT = original_root

            self.assertEqual(code, 0)
            self.assertFalse(
                (target / ".agents" / "skills" / "git-guide").exists(),
                "standalone --purge-legacy must not trigger the default install",
            )

    def test_run_cli_purge_legacy_standalone_errors_exit_nonzero(self) -> None:
        """cr-101: a standalone purge that recorded errors must not exit 0.

        The purge is irreversible removal; a script or CI step gating on the
        exit code must not read a partially-failed purge as success. An
        unwritable .ai/ (chmod 500) makes rmtree fail with EACCES while the
        other legacy paths still purge. Exit 1 matches run_operation's
        errors-recorded convention.
        """
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir(parents=True)
            self._seed_legacy(target)
            legacy_ai = target / ".ai"
            legacy_ai.chmod(0o500)
            try:
                code = mod.run_cli([str(target), "--purge-legacy"])
            finally:
                legacy_ai.chmod(0o755)

            self.assertEqual(code, 1)
            # The unremovable path itself survived; the purge recorded its error.
            self.assertTrue(legacy_ai.is_dir())
            # The other legacy paths still purged.
            self.assertFalse((target / ".cursor" / "skills").exists())

    def test_command_and_skill_selection_do_not_duplicate(self) -> None:
        """A name selected as both skill and command installs exactly once.

        Skills and command-skills share .agents/skills/, so the explicit
        command selection wins and the skill duplicate is dropped.
        """
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            target = Path(tmp) / "target"
            write_command_skill(source, "commit")

            result = mod.install_items(
                source_root=source,
                target_root=target,
                skills=["commit"],
                agents=[],
                commands=["commit"],
                override=False,
            )

            self.assertTrue(result.ok, result.errors)
            self.assertEqual(
                result.installed.count(".agents/skills/cmd-commit"), 1,
                result.installed,
            )
            self.assertNotIn(".agents/skills/cmd-commit", result.skipped)

    def test_bundle_selection_dedupe_drops_skill_duplicate_of_command(self) -> None:
        selection = mod.BundleSelection(
            skills=["commit", "research-guide"],
            commands=["commit"],
        )
        selection.dedupe()
        self.assertEqual(selection.skills, ["research-guide"])
        self.assertEqual(selection.commands, ["commit"])

    def test_run_cli_purge_legacy_composes_with_skills(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            target = Path(tmp) / "target"
            target.mkdir(parents=True)
            skill_dir = source / ".agents" / "skills" / "git-guide"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                "---\nname: git-guide\ndescription: Git operations\n---\n",
                encoding="utf-8",
            )
            self._seed_legacy(target)

            original_root = mod.REPO_ROOT
            mod.REPO_ROOT = source
            try:
                code = mod.run_cli(
                    [str(target), "--purge-legacy", "--skills", "git-guide"]
                )
            finally:
                mod.REPO_ROOT = original_root

            self.assertEqual(code, 0)
            self.assertFalse((target / ".ai").exists())
            self.assertTrue(
                (target / ".agents" / "skills" / "git-guide" / "SKILL.md").is_file()
            )

    def test_run_cli_purge_legacy_compose_purge_errors_exit_nonzero(self) -> None:
        """cr-101: purge+install surfaces purge errors in the exit code.

        A failed purge composed with a successful install must not exit 0:
        the exit code is the only machine-readable signal that the target is
        half-purged. run_operation's errors-recorded convention (exit 1)
        governs. An unwritable .ai/ (chmod 500) fails the purge while the
        install itself succeeds.
        """
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            target = Path(tmp) / "target"
            target.mkdir(parents=True)
            skill_dir = source / ".agents" / "skills" / "git-guide"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                "---\nname: git-guide\ndescription: Git operations\n---\n",
                encoding="utf-8",
            )
            self._seed_legacy(target)
            legacy_ai = target / ".ai"
            legacy_ai.chmod(0o500)
            original_root = mod.REPO_ROOT
            mod.REPO_ROOT = source
            try:
                code = mod.run_cli(
                    [str(target), "--purge-legacy", "--skills", "git-guide"]
                )
            finally:
                mod.REPO_ROOT = original_root
                legacy_ai.chmod(0o755)

            self.assertEqual(code, 1)
            # The install really succeeded (the nonzero exit is the purge's).
            self.assertTrue(
                (target / ".agents" / "skills" / "git-guide" / "SKILL.md").is_file()
            )
            # The purge really failed on this path.
            self.assertTrue(legacy_ai.is_dir())

    def test_run_cli_purge_legacy_requires_target(self) -> None:
        buf = io.StringIO()
        with contextlib.redirect_stderr(buf):
            code = mod.run_cli(["--purge-legacy"])
        self.assertEqual(code, 2)
        self.assertIn("TARGET", buf.getvalue())

class AgentInstallTests(unittest.TestCase):
    """cr-005: agent bulk install pre-checks BOTH dual-target sources."""

    def test_missing_github_agent_source_records_error_and_continues(self) -> None:
        """A missing .github/agents copy must not abort the whole bulk install.

        The loop previously pre-checked only the Claude copy; a missing
        GitHub copy raised InstallerError from copy_path mid-run, skipping
        every remaining name with no per-name error entry.
        """
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            target = Path(tmp) / "target"

            # First agent: complete dual-target source.
            for rel in (".claude/agents/alpha.md", ".github/agents/alpha.agent.md"):
                path = source / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(
                    "---\nname: alpha\ndescription: alpha agent\n---\n",
                    encoding="utf-8",
                )
            # Second agent: GitHub copy missing.
            claude_beta = source / ".claude" / "agents" / "beta.md"
            claude_beta.parent.mkdir(parents=True, exist_ok=True)
            claude_beta.write_text(
                "---\nname: beta\ndescription: beta agent\n---\n",
                encoding="utf-8",
            )

            result = mod.install_items(
                source_root=source,
                target_root=target,
                skills=[],
                agents=["alpha", "beta"],
                commands=[],
                override=False,
            )

            # No exception: the first agent installed, the second recorded a
            # per-name error naming the missing source.
            self.assertFalse(result.ok)
            self.assertTrue(
                (target / ".claude" / "agents" / "alpha.md").is_file(),
                "alpha must still install before beta's error",
            )
            self.assertTrue(
                any("agent beta" in msg for msg in result.errors), result.errors
            )
            self.assertTrue(
                any("beta.agent.md" in msg for msg in result.errors), result.errors
            )

    def test_missing_claude_agent_source_records_error(self) -> None:
        """The missing-source error names whichever source is absent."""
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            target = Path(tmp) / "target"
            github = source / ".github" / "agents" / "alpha.agent.md"
            github.parent.mkdir(parents=True, exist_ok=True)
            github.write_text(
                "---\nname: alpha\ndescription: alpha agent\n---\n",
                encoding="utf-8",
            )

            result = mod.install_items(
                source_root=source,
                target_root=target,
                skills=[],
                agents=["alpha"],
                commands=[],
                override=False,
            )

            self.assertFalse(result.ok)
            self.assertTrue(
                any("alpha.md" in msg for msg in result.errors), result.errors
            )
            self.assertFalse(
                (target / ".github" / "agents" / "alpha.agent.md").exists(),
                "partial pair must not install when the other source is missing",
            )

class CliHelpTextTests(unittest.TestCase):
    """CLI help text reflects the single-root layout (pg-005)."""

    def test_commands_help_mentions_skill_install(self) -> None:
        import contextlib
        import io

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            with self.assertRaises(SystemExit):
                mod.parse_args(["--help"])

        help_text = buf.getvalue()
        # Commands help says they install as command-skills under .agents/skills/.
        # argparse hard-wraps lines, so compare on collapsed whitespace.
        commands_help = " ".join(
            help_text.split("Command names", 1)[1]
            .split("Scripts directory", 1)[0]
            .split()
        )
        self.assertIn(".agents/skills/cmd-<name>/", commands_help)
        self.assertIn("model-invocation", commands_help)
        self.assertNotIn(".github/prompts", commands_help)
        self.assertNotIn(".claude/commands", commands_help)
        self.assertNotIn(".cursor/commands", commands_help)

    def test_purge_legacy_flag_exists(self) -> None:
        import contextlib
        import io

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            with self.assertRaises(SystemExit):
                mod.parse_args(["--help"])

        help_text = " ".join(buf.getvalue().split())
        self.assertIn("--purge-legacy", help_text)
        self.assertIn(".agents/guidelines/", help_text)

    def test_tool_command_files_constant_deleted(self) -> None:
        self.assertFalse(hasattr(mod, "TOOL_COMMAND_FILES"))
        self.assertFalse(hasattr(mod, "TOOL_SKILL_DIRS"))
        self.assertFalse(hasattr(mod, "SHARED_COMMAND_FILE"))
        self.assertFalse(hasattr(mod, "SHARED_AGENT_FILE"))

class DocsCliRemovedTests(unittest.TestCase):
    """The --docs CLI flag is removed (guide travels with the skill)."""

    def test_run_cli_rejects_docs_flag(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir(parents=True, exist_ok=True)

            buf = io.StringIO()
            with contextlib.redirect_stderr(buf):
                with self.assertRaises(SystemExit) as ctx:
                    mod.run_cli([str(target), "--docs", "dev-workflow"])
            self.assertEqual(ctx.exception.code, 2)
            self.assertIn("unrecognized arguments", buf.getvalue())

    def test_resolve_cli_selection_has_no_doc_names(self) -> None:
        import inspect

        signature = inspect.signature(mod.resolve_cli_selection)
        self.assertNotIn("doc_names", signature.parameters)
        selection = mod.resolve_cli_selection(
            bundle_ids=None,
            skill_names=None,
            agent_names=None,
            command_names=None,
            script_names=None,
        )
        self.assertFalse(hasattr(selection, "docs"))

class HeadlessImportTests(unittest.TestCase):
    """t-001/t-002: the CLI must import and function without tkinter.

    The distribution installer's CLI mode must run on hosts without
    python3-tk (containers, minimal WSL); the tkinter import is guarded at
    module level and only the GUI code paths need it.
    """

    def _load_headless(self):
        # Block tkinter (and its submodules) so `import tkinter` raises
        # ImportError in-process; the guard must turn that into None
        # sentinels, not a module-level traceback.
        blocked = {
            name: None
            for name in (
                "tkinter",
                "tkinter.filedialog",
                "tkinter.messagebox",
                "tkinter.scrolledtext",
                "tkinter.ttk",
            )
        }
        stashed = {name: sys.modules.pop(name) for name in blocked if name in sys.modules}
        sys.modules.update(blocked)
        try:
            spec = importlib.util.spec_from_file_location(
                "installer_headless", INSTALLER_PATH
            )
            module = importlib.util.module_from_spec(spec)
            sys.modules["installer_headless"] = module
            spec.loader.exec_module(module)
        finally:
            for name in blocked:
                sys.modules.pop(name, None)
            sys.modules.update(stashed)
        return module

    def test_module_imports_headless(self) -> None:
        module = self._load_headless()
        # The CLI surface functions without touching any GUI path.
        args = module.parse_args(["/tmp/does-not-matter", "--skills", "x"])
        self.assertEqual(args.skills, ["x"])
        self.assertFalse(args.dry_run)

    def test_run_gui_without_tkinter_reports_error(self) -> None:
        module = self._load_headless()
        buf = io.StringIO()
        with contextlib.redirect_stderr(buf):
            with contextlib.redirect_stdout(io.StringIO()):
                # DISPLAY is pinned so the headless branch cannot
                # short-circuit before the tkinter guard fires (pr-003).
                with unittest.mock.patch.dict(os.environ, {"DISPLAY": ":0"}):
                    code = module.run_gui()
        self.assertEqual(code, 2)
        self.assertIn("tkinter", buf.getvalue())

class DryRunTests(unittest.TestCase):
    """t-006..t-008, t-012, t-013: --dry-run previews without mutating.

    A dry run must suppress all six mutation surfaces: copy/remove under
    install, the guidelines write block, the .claude/skills bridge symlink,
    the target mkdir, and every uninstall/purge removal — while all guards
    (cross-kind refusals, provenance checks, exists/skip/override logic)
    evaluate identically to the real run.
    """

    def _fixture(self, root: Path) -> Path:
        """A source catalog with one member of each installable kind."""
        skill = root / ".agents" / "skills" / "sample-skill"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text(
            "---\nname: sample-skill\ndescription: A sample skill.\n---\nbody\n",
            encoding="utf-8",
        )
        cmd = root / ".agents" / "skills" / "cmd-sample-command"
        cmd.mkdir(parents=True)
        (cmd / "SKILL.md").write_text(
            "---\nname: sample-command\ndescription: A sample command.\n"
            "disable-model-invocation: true\n---\nbody\n",
            encoding="utf-8",
        )
        agent_claude = root / ".claude" / "agents"
        agent_github = root / ".github" / "agents"
        agent_claude.mkdir(parents=True)
        agent_github.mkdir(parents=True)
        (agent_claude / "sample-agent.md").write_text(
            "---\nname: sample-agent\ndescription: A sample agent.\n---\nbody\n",
            encoding="utf-8",
        )
        (agent_github / "sample-agent.agent.md").write_text(
            "---\nname: sample-agent\ndescription: A sample agent.\n---\nbody\n",
            encoding="utf-8",
        )
        scripts = root / "tools" / "sample-scripts"
        scripts.mkdir(parents=True)
        (scripts / "README.md").write_text("# sample-scripts\n", encoding="utf-8")
        guideline = root / "guidelines" / "sample-guideline.md"
        guideline.parent.mkdir(parents=True, exist_ok=True)
        guideline.write_text(
            "---\ndescription: A sample guideline.\n---\n# Sample guideline\n",
            encoding="utf-8",
        )
        return root

    def _tree_digest(self, root: Path) -> dict[str, bytes]:
        digest: dict[str, bytes] = {}
        for path in sorted(root.rglob("*")):
            rel = str(path.relative_to(root))
            if path.is_symlink():
                digest[rel] = ("link:" + os.readlink(path)).encode()
            elif path.is_file():
                digest[rel] = path.read_bytes()
            else:
                digest[rel] = b"<dir>"
        return digest

    def _run(self, module, target: Path, source: Path | None = None, **kwargs):
        # run_operation reads the module-global REPO_ROOT; rebind it to the
        # fixture source when one is given (the suite's existing convention).
        original_root = module.REPO_ROOT
        if source is not None:
            module.REPO_ROOT = source
        try:
            return module.run_operation(
                target=target,
                skills=kwargs.get("skills", []),
                agents=kwargs.get("agents", []),
                commands=kwargs.get("commands", []),
                scripts=kwargs.get("scripts", []),
                guidelines=kwargs.get("guidelines", []),
                uninstall=kwargs.get("uninstall", False),
                override=kwargs.get("override", False),
                dry_run=kwargs.get("dry_run", False),
            )
        finally:
            module.REPO_ROOT = original_root

    def test_dry_run_install_leaves_target_untouched(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = self._fixture(Path(tmp) / "source")
            target = Path(tmp) / "target"
            target.mkdir()
            before = self._tree_digest(target)
            code, message = self._run(
                mod,
                target,
                source=source,
                skills=["sample-skill"],
                agents=["sample-agent"],
                commands=["sample-command"],
                scripts=["sample-scripts"],
                guidelines=["sample-guideline"],
                dry_run=True,
            )
            self.assertEqual(code, 0)
            self.assertIn("Would install:", message)
            self.assertEqual(self._tree_digest(target), before)
            self.assertIn(".agents/skills/sample-skill", message)

    def _report_lines(self, message: str) -> set[str]:
        return {
            ln.strip(" -")
            for ln in message.splitlines()
            if ln.startswith("  - ")
        }

    def test_dry_run_matches_real_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = self._fixture(Path(tmp) / "source")
            target = Path(tmp) / "target"
            target.mkdir()
            _, dry_message = self._run(
                mod, target, source=source, skills=["sample-skill"], dry_run=True
            )
            _, real_message = self._run(
                mod, target, source=source, skills=["sample-skill"], dry_run=False
            )
            dry_lines = self._report_lines(dry_message)
            real_lines = self._report_lines(real_message)
            self.assertTrue(dry_lines)
            self.assertEqual(dry_lines, real_lines)

    def test_dry_run_refusal_matches_real_run(self) -> None:
        """cr-002: guard refusals must produce identical error entries
        dry vs real — the cr-004 command-skill-dest refusal fires before
        the dry_run gate, so a preview must report exactly what a real run
        would refuse."""
        with tempfile.TemporaryDirectory() as tmp:
            source = self._fixture(Path(tmp) / "source")
            target = Path(tmp) / "target"
            # A command-skill squatting on the plain-skill name: the cr-004
            # guard refuses the plain-skill install over it, dry or real.
            dest = target / ".agents" / "skills" / "sample-skill"
            dest.mkdir(parents=True)
            (dest / "SKILL.md").write_text(
                "---\nname: sample-skill\ndescription: d.\n"
                "disable-model-invocation: true\n---\nbody\n",
                encoding="utf-8",
            )
            before = self._tree_digest(target)
            dry_code, dry_message = self._run(
                mod, target, source=source, skills=["sample-skill"], dry_run=True
            )
            real_code, real_message = self._run(
                mod, target, source=source, skills=["sample-skill"], dry_run=False
            )
            self.assertEqual(dry_code, real_code)
            self.assertEqual(dry_code, 1)
            self.assertEqual(
                self._report_lines(dry_message), self._report_lines(real_message)
            )
            self.assertIn("refusing to replace command-skill", dry_message)
            self.assertEqual(self._tree_digest(target), before)

    def test_dry_run_requires_existing_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = self._fixture(Path(tmp) / "source")
            target = Path(tmp) / "never-created"
            with self.assertRaises(mod.InstallerError):
                self._run(mod, target, source=source, skills=["sample-skill"], dry_run=True)
            self.assertFalse(target.exists())

    def test_dry_run_purge_reports_without_removing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            legacy = target / ".ai"
            legacy.mkdir(parents=True)
            (legacy / "state.json").write_text("{}", encoding="utf-8")
            before = self._tree_digest(target)
            result = mod.purge_legacy_paths(target, dry_run=True)
            self.assertEqual(result.removed, [".ai"])
            self.assertEqual(self._tree_digest(target), before)

    def test_dry_run_uninstall_reports_without_removing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = self._fixture(Path(tmp) / "source")
            target = Path(tmp) / "target"
            # Real install first, so the uninstall pass has members to remove.
            self._run(
                mod,
                target,
                source=source,
                skills=["sample-skill"],
                agents=["sample-agent"],
                commands=["sample-command"],
                scripts=["sample-scripts"],
                guidelines=["sample-guideline"],
            )
            before = self._tree_digest(target)
            code, message = self._run(
                mod,
                target,
                source=source,
                skills=["sample-skill"],
                agents=["sample-agent"],
                commands=["sample-command"],
                scripts=["sample-scripts"],
                guidelines=["sample-guideline"],
                uninstall=True,
                dry_run=True,
            )
            self.assertEqual(code, 0)
            self.assertEqual(self._tree_digest(target), before)
            for member in (
                ".agents/skills/sample-skill",
                ".claude/agents/sample-agent.md",
                ".agents/skills/cmd-sample-command",
                ".agents/tools/sample-scripts",
                ".agents/skills/guidelines-sample-guideline",
            ):
                self.assertIn(member, message)

    def test_dry_run_uninstall_skips_user_modified_guideline(self) -> None:
        """cr-002: the guideline provenance check must evaluate
        identically under dry-run — a user-modified installed copy is
        reported as skipped (not removed), and the dry run must leave it
        untouched exactly like the real run would."""
        with tempfile.TemporaryDirectory() as tmp:
            source = self._fixture(Path(tmp) / "source")
            target = Path(tmp) / "target"
            self._run(mod, target, source=source, guidelines=["sample-guideline"])
            installed = (
                target
                / ".agents"
                / "skills"
                / "guidelines-sample-guideline"
                / "SKILL.md"
            )
            installed.write_text(
                installed.read_text(encoding="utf-8") + "user-edit\n",
                encoding="utf-8",
            )
            before = self._tree_digest(target)
            code, message = self._run(
                mod,
                target,
                source=source,
                guidelines=["sample-guideline"],
                uninstall=True,
                dry_run=True,
            )
            self.assertEqual(code, 0)
            self.assertEqual(self._tree_digest(target), before)
            self.assertIn(
                ".agents/skills/guidelines-sample-guideline", message
            )
            # The modified copy sits in the skipped section, not Removed.
            removed_section = message.split("Skipped")[0]
            self.assertNotIn(
                ".agents/skills/guidelines-sample-guideline",
                removed_section.split("Dry run")[0],
            )

    def test_dry_run_override_would_replace_without_replacing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = self._fixture(Path(tmp) / "source")
            target = Path(tmp) / "target"
            target.mkdir()
            self._run(mod, target, source=source, skills=["sample-skill"])
            # User modifies the installed copy; a dry-run --override must
            # report the replacement but leave the modified bytes on disk.
            installed_md = (
                target / ".agents" / "skills" / "sample-skill" / "SKILL.md"
            )
            installed_md.write_text("user-modified\n", encoding="utf-8")
            before = self._tree_digest(target)
            code, message = self._run(
                mod, target, source=source, skills=["sample-skill"], override=True, dry_run=True
            )
            self.assertEqual(code, 0)
            self.assertEqual(self._tree_digest(target), before)
            self.assertIn("Would install:", message)
            self.assertEqual(
                installed_md.read_text(encoding="utf-8"), "user-modified\n"
            )

class UninstallMissingTargetTests(unittest.TestCase):
    """cr-001: uninstall on a missing target exits 2, not silent 0.

    validate_target(create=False) owns missing-target handling; a scripted
    teardown of a non-existent project should fail loudly (consistent with
    purge) rather than report an empty success. This pins the deliberate
    exit-code change so it cannot regress unnoticed.
    """

    def test_uninstall_missing_target_exits_2(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "never-created"
            buf = io.StringIO()
            with contextlib.redirect_stderr(buf):
                code = mod.run_cli(
                    [str(target), "--uninstall", "--skills", "sample-skill"]
                )
            self.assertEqual(code, 2)
            self.assertIn("Target project not found", buf.getvalue())


class SelfInstallScriptsGuidelinesTests(unittest.TestCase):
    """C-01 / cr-004: explicit --scripts / --guidelines may target REPO_ROOT; other kinds may not."""

    def test_fresh_clone_bare_install_and_uninstall_refused(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp) / "repo"
            scripts_src = repo_root / "tools" / "dev-workflow"
            scripts_src.mkdir(parents=True)
            (scripts_src / "check.py").write_text("x = 1\n", encoding="utf-8")

            original_root = mod.REPO_ROOT
            mod.REPO_ROOT = repo_root
            try:
                for argv in ([str(repo_root)], [str(repo_root), "--uninstall"]):
                    with self.subTest(argv=argv):
                        err = io.StringIO()
                        with contextlib.redirect_stderr(err):
                            code = mod.run_cli(argv)
                        self.assertEqual(code, 2)
                        self.assertIn("AIConfig repository root", err.getvalue())
                self.assertFalse((repo_root / ".agents").exists())
            finally:
                mod.REPO_ROOT = original_root

    def test_self_install_allows_scripts_and_guidelines_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp) / "repo"
            scripts_src = repo_root / "tools" / "dev-workflow"
            scripts_src.mkdir(parents=True)
            (scripts_src / "check.py").write_text("x = 1\n", encoding="utf-8")
            guideline_src = repo_root / "guidelines" / "response.md"
            guideline_src.parent.mkdir(parents=True)
            guideline_src.write_text(
                "---\ndescription: Response rules.\n---\n# Verdict First\n",
                encoding="utf-8",
            )
            skill_src = repo_root / ".agents" / "skills" / "demo"
            skill_src.mkdir(parents=True)
            (skill_src / "SKILL.md").write_text(
                "---\nname: demo\ndescription: demo.\n---\nbody\n",
                encoding="utf-8",
            )

            original_root = mod.REPO_ROOT
            mod.REPO_ROOT = repo_root
            try:
                code = mod.run_cli(
                    [str(repo_root), "--scripts", "dev-workflow", "--guidelines", "response", "--override"]
                )
                self.assertEqual(code, 0)
                self.assertTrue((repo_root / ".agents" / "tools" / "dev-workflow" / "check.py").is_file())
                self.assertTrue((repo_root / ".agents" / "skills" / "guidelines-response" / "SKILL.md").is_file())

                for argv in (
                    [str(repo_root), "--skills", "demo"],
                    [str(repo_root), "--scripts", "dev-workflow", "--skills", "demo"],
                    [str(repo_root), "--dev-workflow"],
                    [str(repo_root), "--uninstall", "--skills", "demo"],
                    [str(repo_root), "--uninstall", "--scripts", "dev-workflow", "--skills", "demo"],
                    [str(repo_root), "--uninstall"],
                ):
                    with self.subTest(argv=argv):
                        err = io.StringIO()
                        with contextlib.redirect_stderr(err):
                            refused_code = mod.run_cli(argv)
                        self.assertEqual(refused_code, 2)
                        self.assertIn("AIConfig repository root", err.getvalue())

                # Installed self-regenerable targets remain intact until explicitly uninstalled.
                self.assertTrue((repo_root / ".agents" / "tools" / "dev-workflow" / "check.py").is_file())
                self.assertTrue((repo_root / ".agents" / "skills" / "guidelines-response" / "SKILL.md").is_file())

                uninstall_code = mod.run_cli(
                    [str(repo_root), "--uninstall", "--scripts", "dev-workflow", "--guidelines", "response"]
                )
                self.assertEqual(uninstall_code, 0)
                self.assertFalse((repo_root / ".agents" / "tools" / "dev-workflow").exists())
                self.assertFalse((repo_root / ".agents" / "skills" / "guidelines-response").exists())
                self.assertTrue((repo_root / ".agents" / "skills" / "demo" / "SKILL.md").is_file())
            finally:
                mod.REPO_ROOT = original_root

    def test_programmatic_allow_self_defaults_false_and_guards_mixed_kinds(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp) / "repo"
            scripts_src = repo_root / "tools" / "dev-workflow"
            scripts_src.mkdir(parents=True)
            (scripts_src / "check.py").write_text("x = 1\n", encoding="utf-8")

            original_root = mod.REPO_ROOT
            mod.REPO_ROOT = repo_root
            try:
                with self.assertRaises(mod.InstallerError):
                    mod.install_items(
                        source_root=repo_root,
                        target_root=repo_root,
                        skills=(),
                        agents=(),
                        commands=(),
                        scripts=("dev-workflow",),
                    )
                with self.assertRaises(mod.InstallerError):
                    mod.install_items(
                        source_root=repo_root,
                        target_root=repo_root,
                        skills=("demo",),
                        agents=(),
                        commands=(),
                        scripts=("dev-workflow",),
                        allow_self=True,
                    )
                with self.assertRaises(mod.InstallerError):
                    mod.uninstall_items(
                        target_root=repo_root,
                        skills=("demo",),
                        agents=(),
                        commands=(),
                        scripts=("dev-workflow",),
                        allow_self=True,
                    )
            finally:
                mod.REPO_ROOT = original_root


if __name__ == "__main__":
    unittest.main()
