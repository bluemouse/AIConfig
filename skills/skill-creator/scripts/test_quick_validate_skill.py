#!/usr/bin/env python3
"""Tests for skill-creator quick_validate.py single-root .agents/skills validation."""

from __future__ import annotations

import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load module from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


sys.modules.pop("quick_validate", None)
validate_mod = load_module(
    "quick_validate_skill_test", SCRIPTS_DIR / "quick_validate.py"
)

validate_skill = validate_mod.validate_skill
detect_mode = validate_mod.detect_mode
main = validate_mod.main

SKILL_NAME = "test-skill"
SKILL_DESCRIPTION = "Test skill for unit tests."


def skill_md(
    name: str = SKILL_NAME,
    description: str = SKILL_DESCRIPTION,
    body: str = "# Test Skill\n\nShared skill body.\n",
) -> str:
    return f"---\nname: {name}\ndescription: {description}\n---\n\n{body}"


def make_skill(
    parent: Path,
    dirname: str = SKILL_NAME,
    content: str | None = None,
) -> Path:
    skill_dir = parent / dirname
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(content or skill_md(), encoding="utf-8")
    return skill_dir


class FlatRootLayoutTests(unittest.TestCase):
    """Skills must be direct children of a skills root, in both modes."""

    def test_valid_agents_skills_child_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = make_skill(Path(tmp) / ".agents" / "skills")

            valid, message = validate_skill(skill_dir)

            self.assertTrue(valid, msg=message)
            self.assertEqual(message, "Shared skill is valid!")

    def test_bootstrap_skills_child_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = make_skill(Path(tmp) / "skills")

            valid, message = validate_skill(skill_dir)

            self.assertTrue(valid, msg=message)
            self.assertEqual(message, "Bootstrap skill is valid!")

    def test_category_subfolder_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = make_skill(Path(tmp) / ".agents" / "skills" / "category")

            valid, message = validate_skill(skill_dir)

            self.assertFalse(valid)
            self.assertIn("direct child", message)
            self.assertIn("category", message)

    def test_category_subfolder_under_plain_skills_root_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = make_skill(Path(tmp) / "skills" / "category")

            valid, message = validate_skill(skill_dir)

            self.assertFalse(valid)
            self.assertIn("direct child", message)

    def test_dir_without_skills_root_parent_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = make_skill(Path(tmp))

            valid, message = validate_skill(skill_dir)

            self.assertFalse(valid)
            self.assertIn("direct child", message)

    def test_bridge_symlink_path_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_skill(root / ".agents" / "skills")
            (root / ".claude").mkdir()
            os.symlink("../.agents/skills", root / ".claude" / "skills")

            valid, message = validate_skill(root / ".claude" / "skills" / SKILL_NAME)

            self.assertTrue(valid, msg=message)


class KeptChecksTests(unittest.TestCase):
    """Name/dirname and description checks survive the single-root migration."""

    def test_name_dirname_mismatch_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = make_skill(Path(tmp) / "skills", dirname="other-name")

            valid, message = validate_skill(skill_dir)

            self.assertFalse(valid)
            self.assertIn("must match", message)

    def test_description_over_1024_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = make_skill(
                Path(tmp) / "skills",
                content=skill_md(description="x" * 1025),
            )

            valid, message = validate_skill(skill_dir)

            self.assertFalse(valid)
            self.assertIn("1024", message)

    def test_description_at_1024_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = make_skill(
                Path(tmp) / "skills",
                content=skill_md(description="x" * 1024),
            )

            valid, message = validate_skill(skill_dir)

            self.assertTrue(valid, msg=message)

    def test_tool_notes_body_passes(self) -> None:
        body = (
            "# Test Skill\n\nShared skill body.\n\n"
            "## Tool notes\n\n- Claude Code: use the Task tool to dispatch subagents.\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = make_skill(
                Path(tmp) / ".agents" / "skills",
                content=skill_md(body=body),
            )

            valid, message = validate_skill(skill_dir)

            self.assertTrue(valid, msg=message)


class ModeAndDeadCodeTests(unittest.TestCase):
    """Modes reduce to bootstrap-source + shared/installed; wrapper mode is gone."""

    def test_wrapper_symbols_removed(self) -> None:
        for symbol in ("validate_wrapper_skill", "expected_shared_reference"):
            self.assertFalse(
                hasattr(validate_mod, symbol),
                msg=f"quick_validate.py still defines wrapper-mode symbol: {symbol}",
            )
        for symbol in ("validate_skill", "validate_shared_skill", "detect_mode"):
            self.assertTrue(
                hasattr(validate_mod, symbol),
                msg=f"quick_validate.py lost kept symbol: {symbol}",
            )

    def test_detect_mode_covers_bootstrap_and_shared_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bootstrap = make_skill(root / "skills")
            shared = make_skill(root / ".agents" / "skills")

            self.assertEqual(detect_mode(bootstrap), "bootstrap")
            self.assertEqual(detect_mode(shared), "shared")
            self.assertEqual(tuple(validate_mod.SKILL_MODES), ("bootstrap", "shared"))

    def test_explicit_mode_overrides_detection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = make_skill(Path(tmp) / "skills")

            valid, message = validate_skill(skill_dir, "shared")

            self.assertTrue(valid, msg=message)
            self.assertEqual(message, "Shared skill is valid!")

    def test_cli_rejects_wrapper_mode(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = make_skill(Path(tmp) / "skills")

            with self.assertRaises(SystemExit) as ctx:
                main(["--mode", "wrapper", str(skill_dir)])

            self.assertEqual(ctx.exception.code, 2)


class CliTests(unittest.TestCase):
    def test_main_valid_skill_returns_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = make_skill(Path(tmp) / ".agents" / "skills")

            self.assertEqual(main([str(skill_dir)]), 0)

    def test_main_category_subfolder_returns_one(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = make_skill(Path(tmp) / ".agents" / "skills" / "category")

            self.assertEqual(main([str(skill_dir)]), 1)


if __name__ == "__main__":
    unittest.main()
