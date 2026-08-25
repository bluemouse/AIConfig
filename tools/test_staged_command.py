#!/usr/bin/env python3
"""Tests for /dev-workflow command stage-aware mode detection (pg-008).

Validates:
- t-010: /dev-workflow COMMAND.md documents reading Execution mode from the plan
"""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
COMMAND_PATH = REPO_ROOT / "commands" / "dev-workflow" / "COMMAND.md"


class StagedCommandTests(unittest.TestCase):
    """t-010: /dev-workflow command detects staged mode."""

    def test_command_detects_staged_mode(self) -> None:
        """t-010: /dev-workflow COMMAND.md documents reading Execution mode from the plan."""
        self.assertTrue(COMMAND_PATH.is_file(), f"COMMAND.md not found at {COMMAND_PATH}")
        text = COMMAND_PATH.read_text(encoding="utf-8")
        self.assertTrue(
            "Execution mode" in text or "staged" in text.lower(),
            "/dev-workflow COMMAND.md must document reading Execution mode from the plan "
            "to detect staged mode",
        )


if __name__ == "__main__":
    unittest.main()
