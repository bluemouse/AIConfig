#!/usr/bin/env python3
"""Tests for the per-phase dev-workflow command bootstrap sources.

Validates that the four `/dev-workflow-<phase>` commands exist as bootstrap
sources under `commands/dev-workflow-<phase>/COMMAND.md`, have valid
frontmatter, and contain no tool-specific content in the shared body.
"""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
COMMAND_CREATOR_SCRIPTS = REPO_ROOT / "skills" / "command-creator" / "scripts"

# Load quick_validate as a module (it lives outside the tools/ package).
_spec = importlib.util.spec_from_file_location(
    "quick_validate", COMMAND_CREATOR_SCRIPTS / "quick_validate.py"
)
if _spec is None or _spec.loader is None:
    raise RuntimeError(f"Could not load quick_validate from {COMMAND_CREATOR_SCRIPTS}")
quick_validate = importlib.util.module_from_spec(_spec)
sys.modules["quick_validate"] = quick_validate
_spec.loader.exec_module(quick_validate)


PHASE_COMMANDS = (
    "dev-workflow-research",
    "dev-workflow-plan",
    "dev-workflow-implement",
    "dev-workflow-review",
)


def _command_md_path(name: str) -> Path:
    return REPO_ROOT / "commands" / name / "COMMAND.md"


class CommandBootstrapFilesTests(unittest.TestCase):
    def test_command_bootstrap_files_exist(self) -> None:
        """All four per-phase COMMAND.md bootstrap files must exist."""
        for name in PHASE_COMMANDS:
            path = _command_md_path(name)
            self.assertTrue(
                path.is_file(),
                f"Missing bootstrap COMMAND.md for {name}: expected at {path}",
            )

    def test_command_frontmatter_valid(self) -> None:
        """Each COMMAND.md must have valid frontmatter with name and description."""
        for name in PHASE_COMMANDS:
            path = _command_md_path(name)
            if not path.is_file():
                self.fail(f"COMMAND.md missing for {name}: {path}")
            content = path.read_text(encoding="utf-8")
            frontmatter, error = quick_validate.parse_frontmatter(content)
            self.assertIsNone(error, f"Invalid frontmatter in {path}: {error}")
            assert frontmatter is not None  # for type checkers
            self.assertEqual(
                frontmatter.get("name"),
                name,
                f"Frontmatter 'name' in {path} should be '{name}', "
                f"got {frontmatter.get('name')!r}",
            )
            description = str(frontmatter.get("description", "")).strip()
            self.assertTrue(
                description,
                f"Frontmatter 'description' in {path} must be non-empty",
            )

    def test_command_body_tool_neutral(self) -> None:
        """Shared COMMAND.md bodies must not contain tool-specific patterns."""
        for name in PHASE_COMMANDS:
            path = _command_md_path(name)
            if not path.is_file():
                self.fail(f"COMMAND.md missing for {name}: {path}")
            content = path.read_text(encoding="utf-8")
            body = quick_validate.body_after_frontmatter(content)
            for pattern in quick_validate.TOOL_NEUTRALITY_PATTERNS:
                match = pattern.search(body)
                self.assertIsNone(
                    match,
                    f"Tool-specific pattern {pattern.pattern!r} found in {path} body: "
                    f"{match.group(0) if match else ''}",
                )


if __name__ == "__main__":
    unittest.main()
