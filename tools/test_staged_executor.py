#!/usr/bin/env python3
"""Tests for plan-executor single-stage execution scope (pg-004).

Validates:
- t-009: plan-executor SKILL.md documents accepting a stage scope parameter

Note: This is a documentation-presence test (grep for text in the markdown
skill file), not a behavior test, because plan-executor is a markdown skill.
"""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLAN_EXECUTOR_PATH = REPO_ROOT / "skills" / "plan-executor" / "SKILL.md"


class StagedExecutorTests(unittest.TestCase):
    """t-009: plan-executor accepts a stage scope parameter."""

    def test_executor_accepts_stage_scope(self) -> None:
        """t-009: plan-executor SKILL.md documents accepting a stage scope parameter."""
        self.assertTrue(
            PLAN_EXECUTOR_PATH.is_file(),
            f"plan-executor not found at {PLAN_EXECUTOR_PATH}",
        )
        text = PLAN_EXECUTOR_PATH.read_text(encoding="utf-8")
        # The skill should document stage-scoped execution
        self.assertTrue(
            "stage" in text.lower() and "scope" in text.lower(),
            "plan-executor SKILL.md must document stage-scoped execution "
            "(accepting a stage parameter to execute one stage's tasks)",
        )


if __name__ == "__main__":
    unittest.main()
