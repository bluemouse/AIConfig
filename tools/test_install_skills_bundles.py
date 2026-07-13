#!/usr/bin/env python3
"""Tests for bundle loading and CLI skill resolution in install-skills.py."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
INSTALL_SKILLS_PATH = TOOLS_DIR / "install-skills.py"
BUNDLES_JSON_PATH = TOOLS_DIR / "bundles.json"


def load_install_skills_module():
    spec = importlib.util.spec_from_file_location("install_skills", INSTALL_SKILLS_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load module from {INSTALL_SKILLS_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["install_skills"] = module
    spec.loader.exec_module(module)
    return module


mod = load_install_skills_module()


def write_bundle_config(data: dict) -> Path:
    handle = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
    json.dump(data, handle)
    handle.close()
    return Path(handle.name)


class BundleLoadingTests(unittest.TestCase):
    def test_load_production_bundles(self) -> None:
        bundles = mod.load_skill_bundles(BUNDLES_JSON_PATH)
        by_id = {bundle.id: bundle for bundle in bundles}
        self.assertEqual(len(by_id["core-dev-workflow"].skills), 10)
        self.assertEqual(len(by_id["extended-dev-workflow"].skills), 15)

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
            with self.assertRaises(mod.InstallSkillsError) as ctx:
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
            with self.assertRaises(mod.InstallSkillsError) as ctx:
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
        self.assertEqual(resolved, all_skills)

    def test_resolve_cli_skills_bundle_only(self) -> None:
        resolved = mod.resolve_cli_skills(
            bundle_ids=["core-dev-workflow"],
            skill_names=None,
        )
        self.assertEqual(len(resolved), 10)

    def test_resolve_cli_skills_union(self) -> None:
        resolved = mod.resolve_cli_skills(
            bundle_ids=["core-dev-workflow"],
            skill_names=["cpp-coding", "research-guide"],
        )
        self.assertIn("cpp-coding", resolved)
        self.assertIn("research-guide", resolved)
        self.assertEqual(len(resolved), 11)

    def test_unknown_bundle_id(self) -> None:
        with self.assertRaises(mod.InstallSkillsError) as ctx:
            mod.resolve_cli_skills(bundle_ids=["nope"], skill_names=None)
        message = str(ctx.exception)
        self.assertIn("Unknown bundle", message)
        self.assertIn("core-dev-workflow", message)


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
