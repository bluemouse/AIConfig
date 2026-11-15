#!/usr/bin/env python3
"""Tests for bundle loading and CLI skill resolution in installer.py."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

TOOLS_DIR = Path(__file__).resolve().parent
INSTALLER_PATH = TOOLS_DIR / "installer.py"
BUNDLES_JSON_PATH = TOOLS_DIR / "bundles.json"


def load_installer_module():
    spec = importlib.util.spec_from_file_location("installer", INSTALLER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load module from {INSTALLER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["installer"] = module
    spec.loader.exec_module(module)
    return module


mod = load_installer_module()


def write_bundle_config(data: dict) -> Path:
    handle = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
    json.dump(data, handle)
    handle.close()
    return Path(handle.name)


class BundleLoadingTests(unittest.TestCase):
    def test_load_production_bundles(self) -> None:
        bundles = mod.load_skill_bundles(BUNDLES_JSON_PATH)
        by_id = {bundle.id: bundle for bundle in bundles}
        self.assertEqual(len(by_id["core-dev-workflow"].skills), 12)
        self.assertEqual(len(by_id["extended-dev-workflow"].skills), 21)
        self.assertIn("git-merge-guide", by_id["extended-dev-workflow"].skills)

    def test_load_dev_workflow_harness_bundle(self) -> None:
        bundles = mod.load_skill_bundles(BUNDLES_JSON_PATH)
        by_id = {bundle.id: bundle for bundle in bundles}
        harness = by_id["dev-workflow-harness"]
        self.assertEqual(
            harness.skills,
            frozenset({
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
            }),
        )
        self.assertEqual(
            harness.commands,
            frozenset({
                "dev-workflow",
                "dev-workflow-research",
                "dev-workflow-plan",
                "dev-workflow-implement",
                "dev-workflow-review",
            }),
        )
        self.assertEqual(harness.scripts, frozenset({"dev-workflow"}))
        self.assertEqual(
            harness.agents,
            frozenset({
                "research-reviewer",
                "plan-reviewer",
                "implementation-auditor",
                "code-reviewer",
            }),
        )

    def test_bases_composition(self) -> None:
        config = {
            "version": 2,
            "bases": [
                {
                    "id": "core-dev-workflow",
                    "skills": ["research-guide", "plan-guide"],
                }
            ],
            "bundles": [
                {
                    "id": "core-dev-workflow",
                    "name": "Core",
                    "description": "Core bundle",
                    "bases": ["core-dev-workflow"],
                },
                {
                    "id": "extended-dev-workflow",
                    "name": "Extended",
                    "description": "Extended bundle",
                    "bases": ["core-dev-workflow"],
                    "skills": ["debugging-guide"],
                },
            ],
        }
        path = write_bundle_config(config)
        try:
            bundles = mod.load_skill_bundles(path)
            by_id = {bundle.id: bundle for bundle in bundles}
            self.assertEqual(by_id["core-dev-workflow"].skills, frozenset({"research-guide", "plan-guide"}))
            self.assertEqual(
                by_id["extended-dev-workflow"].skills,
                frozenset({"research-guide", "plan-guide", "debugging-guide"}),
            )
        finally:
            path.unlink()

    def test_unknown_base_reference(self) -> None:
        config = {
            "bundles": [
                {
                    "id": "broken",
                    "name": "Broken",
                    "description": "Broken bundle",
                    "bases": ["missing-base"],
                }
            ]
        }
        path = write_bundle_config(config)
        try:
            with self.assertRaises(mod.InstallerError) as ctx:
                mod.load_skill_bundles(path)
            self.assertIn("unknown base", str(ctx.exception))
        finally:
            path.unlink()

    def test_duplicate_base_id(self) -> None:
        config = {
            "bases": [
                {"id": "dup", "skills": ["git-guide"]},
                {"id": "dup", "skills": ["git-guide"]},
            ],
            "bundles": [
                {
                    "id": "bundle",
                    "name": "Bundle",
                    "description": "Bundle",
                    "bases": ["dup"],
                }
            ],
        }
        path = write_bundle_config(config)
        try:
            with self.assertRaises(mod.InstallerError) as ctx:
                mod.load_skill_bundles(path)
            self.assertIn("duplicate base id", str(ctx.exception))
        finally:
            path.unlink()

    def test_slugified_base_reference(self) -> None:
        config = {
            "bases": [
                {
                    "id": "Core-Dev-Workflow",
                    "skills": ["research-guide"],
                }
            ],
            "bundles": [
                {
                    "id": "workflow",
                    "name": "Workflow",
                    "description": "Workflow bundle",
                    "bases": ["core-dev-workflow"],
                }
            ],
        }
        path = write_bundle_config(config)
        try:
            bundles = mod.load_skill_bundles(path)
            self.assertEqual(bundles[0].skills, frozenset({"research-guide"}))
        finally:
            path.unlink()


class CliSkillResolutionTests(unittest.TestCase):
    def test_resolve_cli_skills_default(self) -> None:
        """Default skill resolution lists every discovered skill, but a
        command-skill name is deduped out of the SKILLS list (fd-019: the
        default branch dedupes like the explicit-selection path — the
        command keeps the name; the skills list drops the duplicate so the
        default uninstall/install never processes one name as both kinds)."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            original_root = mod.REPO_ROOT
            root = Path(tmp)
            # A command-skill and a plain skill sharing the discovered tree.
            skill_dir = root / ".agents" / "skills" / "demo"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                "---\nname: demo\ndescription: d\ndisable-model-invocation: true\n---\n\n# demo\n",
                encoding="utf-8",
            )
            plain_dir = root / ".agents" / "skills" / "plain"
            plain_dir.mkdir(parents=True)
            (plain_dir / "SKILL.md").write_text(
                "---\nname: plain\ndescription: d\n---\n\n# plain\n",
                encoding="utf-8",
            )
            mod.REPO_ROOT = root
            try:
                resolved = mod.resolve_cli_skills(bundle_ids=None, skill_names=None)
                commands = mod.resolve_cli_selection(
                    bundle_ids=None,
                    skill_names=None,
                    agent_names=None,
                    command_names=None,
                    script_names=None,
                ).commands
            finally:
                mod.REPO_ROOT = original_root

            self.assertEqual(resolved, ["plain"])
            self.assertEqual(commands, ["demo"])

    def test_resolve_cli_skills_default_is_unfiltered(self) -> None:
        """fr-7 (t-109): no exclusion mechanism — every discovered skill is selected.

        A fixture skill named verdict-first under a temp REPO_ROOT makes the
        red phase genuine: the pre-removal filter excludes it.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for rel in (
                ".agents/skills/verdict-first/SKILL.md",
                ".agents/skills/verdict-first/EXTRA.md",
            ):
                path = root / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(
                    "---\nname: verdict-first\ndescription: probe\n---\n",
                    encoding="utf-8",
                )
            original_root = mod.REPO_ROOT
            mod.REPO_ROOT = root
            try:
                resolved = mod.resolve_cli_skills(bundle_ids=None, skill_names=None)
            finally:
                mod.REPO_ROOT = original_root

            self.assertIn("verdict-first", resolved)

    def test_discover_skills_scans_agents_skills(self) -> None:
        """t-014a: skills are discovered from .agents/skills/."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill_dir = root / ".agents" / "skills" / "alpha"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                "---\nname: alpha\ndescription: probe\n---\n", encoding="utf-8"
            )
            original_root = mod.REPO_ROOT
            mod.REPO_ROOT = root
            try:
                discovered = mod.discover_skills()
            finally:
                mod.REPO_ROOT = original_root

            self.assertEqual(discovered, ["alpha"])

    def test_discover_agents_reads_both_files(self) -> None:
        """t-014a: agents are discovered from both dual-target files."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            claude = root / ".claude" / "agents"
            claude.mkdir(parents=True)
            (claude / "alpha.md").write_text(
                "---\nname: alpha\ndescription: probe\n---\n", encoding="utf-8"
            )
            (claude / "beta.md").write_text(
                "---\nname: beta\ndescription: probe\n---\n", encoding="utf-8"
            )
            github = root / ".github" / "agents"
            github.mkdir(parents=True)
            (github / "beta.agent.md").write_text(
                "---\nname: beta\ndescription: probe\n---\n", encoding="utf-8"
            )
            original_root = mod.REPO_ROOT
            mod.REPO_ROOT = root
            try:
                discovered = mod.discover_agents()
            finally:
                mod.REPO_ROOT = original_root

            self.assertEqual(discovered, ["alpha", "beta"])

    def test_discover_commands_filters_command_skills(self) -> None:
        """t-014a: commands are the command-skills — flag-filtered from
        .agents/skills/ — so the --commands selector keeps functioning."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            command_dir = root / ".agents" / "skills" / "git-commit"
            command_dir.mkdir(parents=True)
            (command_dir / "SKILL.md").write_text(
                "---\n"
                "name: git-commit\n"
                "description: Write commit messages\n"
                "disable-model-invocation: true\n"
                "---\n",
                encoding="utf-8",
            )
            plain_dir = root / ".agents" / "skills" / "plain-skill"
            plain_dir.mkdir(parents=True)
            (plain_dir / "SKILL.md").write_text(
                "---\nname: plain-skill\ndescription: probe\n---\n",
                encoding="utf-8",
            )
            original_root = mod.REPO_ROOT
            mod.REPO_ROOT = root
            try:
                commands = mod.discover_commands()
                # A --commands selection resolves only command-skills.
                selection = mod.resolve_cli_selection(
                    bundle_ids=None,
                    skill_names=None,
                    agent_names=None,
                    command_names=["git-commit"],
                    script_names=None,
                )
            finally:
                mod.REPO_ROOT = original_root

            self.assertEqual(commands, ["git-commit"])
            self.assertEqual(selection.commands, ["git-commit"])

    def test_discover_scripts_scans_agents_tools(self) -> None:
        """t-014a: scripts are discovered from .agents/tools/."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tools_dir = root / ".agents" / "tools" / "dev-workflow"
            tools_dir.mkdir(parents=True)
            (tools_dir / "README.md").write_text("# dev-workflow\n", encoding="utf-8")
            original_root = mod.REPO_ROOT
            mod.REPO_ROOT = root
            try:
                discovered = mod.discover_scripts()
            finally:
                mod.REPO_ROOT = original_root

            self.assertEqual(discovered, ["dev-workflow"])

    def test_no_default_exclusion_mechanism_remains(self) -> None:
        """fr-7 (t-108): the personal-preference exclusion mechanism is gone."""
        self.assertFalse(hasattr(mod, "DEFAULT_EXCLUDED_SKILLS"))

    def test_personal_output_bundle_removed(self) -> None:
        """fr-6 (t-107): the personal-output bundle no longer exists."""
        with self.assertRaisesRegex(
            mod.InstallerError, r"Unknown bundle 'personal-output'"
        ):
            mod.resolve_cli_skills(
                bundle_ids=["personal-output"],
                skill_names=None,
            )

    def test_resolve_cli_skills_bundle_only(self) -> None:
        resolved = mod.resolve_cli_skills(
            bundle_ids=["core-dev-workflow"],
            skill_names=None,
        )
        self.assertEqual(len(resolved), 12)

    def test_resolve_cli_skills_union(self) -> None:
        resolved = mod.resolve_cli_skills(
            bundle_ids=["core-dev-workflow"],
            skill_names=["cpp-coding", "research-guide"],
        )
        self.assertIn("cpp-coding", resolved)
        self.assertIn("research-guide", resolved)
        self.assertEqual(len(resolved), 13)

    def test_unknown_bundle_id(self) -> None:
        with self.assertRaises(mod.InstallerError) as ctx:
            mod.resolve_cli_skills(bundle_ids=["nope"], skill_names=None)
        message = str(ctx.exception)
        self.assertIn("Unknown bundle", message)
        self.assertIn("core-dev-workflow", message)
        self.assertIn(mod.TARGET_BUNDLE_ID, message)


class DocsBundleMembershipRemovedTests(unittest.TestCase):
    """The docs bundle member kind is removed (guide travels with the skill)."""

    def test_harness_bundle_has_no_docs_members(self) -> None:
        bundles = mod.load_skill_bundles(BUNDLES_JSON_PATH)
        by_id = {bundle.id: bundle for bundle in bundles}
        for bundle in bundles:
            self.assertFalse(
                hasattr(bundle, "docs"),
                f"Bundle {bundle.id} must not carry a docs attribute",
            )
        self.assertIn("dev-workflow-harness", by_id)

    def test_bundle_config_has_no_docs_keys(self) -> None:
        """bundles.json must not declare docs members anywhere — the docs
        install kind is gone, so a docs key would silently no-op."""
        import json

        payload = json.loads(BUNDLES_JSON_PATH.read_text(encoding="utf-8"))
        for entry in payload.get("bases", []) + payload.get("bundles", []):
            self.assertNotIn(
                "docs",
                entry,
                f"{entry.get('id', entry)} still declares a docs member list",
            )


class TargetBundleTests(unittest.TestCase):
    def _write_target_skill(self, root: Path, name: str) -> None:
        skill_dir = root / ".agents" / "skills" / name
        skill_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: {name} skill\n---\n",
            encoding="utf-8",
        )

    def _write_target_agent(self, root: Path, name: str) -> None:
        agents_dir = root / ".claude" / "agents"
        agents_dir.mkdir(parents=True, exist_ok=True)
        (agents_dir / f"{name}.md").write_text(
            f"---\nname: {name}\ndescription: {name} agent\n---\n",
            encoding="utf-8",
        )

    def _write_target_command(self, root: Path, name: str) -> None:
        skill_dir = root / ".agents" / "skills" / name
        skill_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / "SKILL.md").write_text(
            f"---\n"
            f"name: {name}\n"
            f"description: {name} command\n"
            "disable-model-invocation: true\n"
            "---\n",
            encoding="utf-8",
        )

    def _write_target_scripts(self, root: Path, name: str) -> None:
        scripts_dir = root / ".agents" / "tools" / name
        scripts_dir.mkdir(parents=True, exist_ok=True)
        (scripts_dir / "README.md").write_text(f"# {name}\n", encoding="utf-8")

    def test_discover_skills_in_project(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_target_skill(root, "alpha")
            self._write_target_skill(root, "beta")
            (root / ".agents" / "skills" / "empty").mkdir(parents=True)
            self.assertEqual(mod.discover_skills_in_project(root), ["alpha", "beta"])

    def test_discover_skills_in_project_missing_shared(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(mod.discover_skills_in_project(Path(tmp)), [])

    def test_build_target_bundle_intersection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_target_skill(root, "alpha")
            self._write_target_skill(root, "beta")
            self._write_target_skill(root, "only-in-target")
            bundle = mod.build_target_bundle(
                root,
                available_skills=["alpha", "beta", "gamma"],
            )
            self.assertEqual(bundle.id, mod.TARGET_BUNDLE_ID)
            self.assertEqual(bundle.name, mod.TARGET_BUNDLE_NAME)
            self.assertEqual(bundle.skills, frozenset({"alpha", "beta"}))

    def test_resolve_target_bundle_skills(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_target_skill(root, "research-guide")
            with mock.patch.object(
                mod, "discover_skills", return_value=["research-guide", "other"]
            ):
                self.assertEqual(
                    mod.resolve_target_bundle_skills(root),
                    ["research-guide"],
                )

    def test_resolve_bundle_skills_target_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_target_skill(root, "research-guide")
            with mock.patch.object(
                mod, "discover_skills", return_value=["research-guide", "other"]
            ):
                resolved = mod.resolve_bundle_skills(
                    [mod.TARGET_BUNDLE_ID],
                    target_root=root,
                )
            self.assertEqual(resolved, ["research-guide"])

    def test_resolve_bundle_skills_target_bundle_requires_target(self) -> None:
        with self.assertRaises(mod.InstallerError) as ctx:
            mod.resolve_bundle_skills([mod.TARGET_BUNDLE_ID], target_root=None)
        self.assertIn("requires a target project path", str(ctx.exception))

    def test_known_bundle_ids_includes_target_bundle(self) -> None:
        ids = mod.known_bundle_ids(BUNDLES_JSON_PATH)
        self.assertIn(mod.TARGET_BUNDLE_ID, ids)
        self.assertIn("core-dev-workflow", ids)

    def test_resolve_cli_skills_target_bundle_empty_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(mod.InstallerError) as ctx:
                mod.resolve_cli_skills(
                    bundle_ids=["target-bundle"],
                    skill_names=None,
                    target_root=Path(tmp),
                )
            self.assertIn("no matching installed members", str(ctx.exception))

    def test_discover_agents_in_project(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_target_agent(root, "alpha")
            self._write_target_agent(root, "beta")
            (root / ".claude" / "agents" / ".hidden.md").write_text("x", encoding="utf-8")
            self.assertEqual(mod.discover_agents_in_project(root), ["alpha", "beta"])

    def test_discover_agents_in_project_missing_shared(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(mod.discover_agents_in_project(Path(tmp)), [])

    def test_discover_commands_in_project(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_target_command(root, "alpha")
            self._write_target_command(root, "beta")
            self.assertEqual(mod.discover_commands_in_project(root), ["alpha", "beta"])

    def test_discover_commands_in_project_missing_shared(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(mod.discover_commands_in_project(Path(tmp)), [])

    def test_discover_scripts_in_project(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_target_scripts(root, "alpha")
            self._write_target_scripts(root, "beta")
            (root / ".agents" / "tools" / "__pycache__").mkdir(parents=True)
            self.assertEqual(mod.discover_scripts_in_project(root), ["alpha", "beta"])

    def test_discover_scripts_in_project_missing_shared(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(mod.discover_scripts_in_project(Path(tmp)), [])

    def test_build_target_bundle_includes_all_kinds(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_target_skill(root, "alpha")
            self._write_target_skill(root, "only-in-target")
            self._write_target_agent(root, "alpha")
            self._write_target_command(root, "alpha")
            self._write_target_scripts(root, "alpha")
            bundle = mod.build_target_bundle(
                root,
                available_skills=["alpha", "beta"],
                available_agents=["alpha", "beta"],
                available_commands=["alpha", "beta"],
                available_scripts=["alpha", "beta"],
            )
            self.assertEqual(bundle.skills, frozenset({"alpha"}))
            self.assertEqual(bundle.agents, frozenset({"alpha"}))
            self.assertEqual(bundle.commands, frozenset({"alpha"}))
            self.assertEqual(bundle.scripts, frozenset({"alpha"}))
            self.assertFalse(bundle.is_empty)

    def test_build_target_bundle_empty_when_no_matches(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_target_skill(root, "only-in-target")
            self._write_target_agent(root, "only-in-target")
            bundle = mod.build_target_bundle(
                root,
                available_skills=["alpha"],
                available_agents=["alpha"],
                available_commands=["alpha"],
                available_scripts=["alpha"],
            )
            self.assertTrue(bundle.is_empty)

    def test_resolve_bundle_target_bundle_includes_all_kinds(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_target_skill(root, "research-guide")
            self._write_target_agent(root, "alpha")
            self._write_target_command(root, "git-commit")
            self._write_target_scripts(root, "dev-workflow")
            with mock.patch.object(mod, "discover_skills", return_value=["research-guide"]), \
                 mock.patch.object(mod, "discover_agents", return_value=["alpha"]), \
                 mock.patch.object(mod, "discover_commands", return_value=["git-commit"]), \
                 mock.patch.object(mod, "discover_scripts", return_value=["dev-workflow"]):
                selection = mod.resolve_bundle(
                    [mod.TARGET_BUNDLE_ID],
                    target_root=root,
                )
            self.assertIn("research-guide", selection.skills)
            self.assertIn("alpha", selection.agents)
            self.assertIn("git-commit", selection.commands)
            self.assertIn("dev-workflow", selection.scripts)

    def test_resolve_cli_skills_target_bundle_with_other_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            resolved = mod.resolve_cli_skills(
                bundle_ids=["target-bundle", "core-dev-workflow"],
                skill_names=None,
                target_root=Path(tmp),
            )
            self.assertEqual(len(resolved), 12)

    def test_resolve_cli_skills_explicit_bundles_no_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_target_skill(root, "research-guide")
            with mock.patch.object(
                mod, "discover_skills", return_value=["research-guide", "other"]
            ):
                resolved = mod.resolve_cli_skills(
                    bundle_ids=["target-bundle"],
                    skill_names=None,
                    target_root=root,
                )
            self.assertEqual(resolved, ["research-guide"])


class BundleSelectionStateTests(unittest.TestCase):
    def test_bundle_selection_state(self) -> None:
        members = ["a", "b", "c"]
        self.assertEqual(
            mod.bundle_selection_state(members, lambda name: True),
            "all",
        )
        self.assertEqual(
            mod.bundle_selection_state(members, lambda name: False),
            "none",
        )
        self.assertEqual(
            mod.bundle_selection_state(members, lambda name: name == "a"),
            "partial",
        )

    def test_bundle_toggle_target_state(self) -> None:
        self.assertFalse(mod.bundle_toggle_target_state("all"))
        self.assertTrue(mod.bundle_toggle_target_state("none"))
        self.assertTrue(mod.bundle_toggle_target_state("partial"))


if __name__ == "__main__":
    unittest.main()
