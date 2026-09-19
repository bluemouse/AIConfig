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
        all_skills = mod.discover_skills()
        resolved = mod.resolve_cli_skills(bundle_ids=None, skill_names=None)
        expected = [name for name in all_skills if name not in mod.DEFAULT_EXCLUDED_SKILLS]
        self.assertEqual(resolved, expected)

    def test_resolve_cli_skills_default_excludes_personal_skills(self) -> None:
        resolved = mod.resolve_cli_skills(bundle_ids=None, skill_names=None)
        self.assertNotIn("verdict-first", resolved)
        self.assertIn("commit-message-writer", resolved)

    def test_resolve_cli_skills_explicit_personal_skill_installs(self) -> None:
        resolved = mod.resolve_cli_skills(
            bundle_ids=None,
            skill_names=["verdict-first"],
        )
        self.assertEqual(resolved, ["verdict-first"])

    def test_resolve_cli_skills_personal_bundle_installs(self) -> None:
        resolved = mod.resolve_cli_skills(
            bundle_ids=["personal-output"],
            skill_names=None,
        )
        self.assertEqual(resolved, ["verdict-first"])

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


class TargetBundleTests(unittest.TestCase):
    def _write_target_skill(self, root: Path, name: str) -> None:
        skill_dir = root / ".ai" / "skills" / name
        skill_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: {name} skill\n---\n",
            encoding="utf-8",
        )

    def _write_target_agent(self, root: Path, name: str) -> None:
        agents_dir = root / ".ai" / "agents"
        agents_dir.mkdir(parents=True, exist_ok=True)
        (agents_dir / f"{name}.md").write_text(
            f"---\nname: {name}\ndescription: {name} agent\n---\n",
            encoding="utf-8",
        )

    def _write_target_command(self, root: Path, name: str) -> None:
        commands_dir = root / ".ai" / "commands"
        commands_dir.mkdir(parents=True, exist_ok=True)
        (commands_dir / f"{name}.md").write_text(
            f"---\nname: {name}\ndescription: {name} command\n---\n",
            encoding="utf-8",
        )

    def _write_target_scripts(self, root: Path, name: str) -> None:
        scripts_dir = root / ".ai" / "tools" / name
        scripts_dir.mkdir(parents=True, exist_ok=True)
        (scripts_dir / "README.md").write_text(f"# {name}\n", encoding="utf-8")

    def test_discover_skills_in_project(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_target_skill(root, "alpha")
            self._write_target_skill(root, "beta")
            (root / ".ai" / "skills" / "empty").mkdir(parents=True)
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
            self.assertEqual(
                mod.resolve_target_bundle_skills(root),
                ["research-guide"],
            )

    def test_resolve_bundle_skills_target_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_target_skill(root, "research-guide")
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
            (root / ".ai" / "agents" / ".hidden.md").write_text("x", encoding="utf-8")
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
            (root / ".ai" / "tools" / "__pycache__").mkdir(parents=True)
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
