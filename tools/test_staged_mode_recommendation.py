#!/usr/bin/env python3
"""Tests for plan-guide staged-mode recommendation (pg-002).

Validates:
- t-003: plan-guide recommends staged mode when planning depth = rigorous
- t-003b: plan-guide recommends staged mode when task count > 5
- t-003c: plan-guide does NOT recommend staged mode for single-stage plans (fr-14)

Note: These are documentation-presence tests (grep for text in the markdown
skill file), not behavior tests, because plan-guide is a markdown skill.
"""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLAN_GUIDE_PATH = REPO_ROOT / "skills" / "plan-guide" / "SKILL.md"


class StagedModeRecommendationTests(unittest.TestCase):
    """t-003, t-003b, t-003c: plan-guide mode recommendation logic."""

    def test_recommend_staged_for_rigorous_depth(self) -> None:
        """t-003: plan-guide recommends staged when depth = rigorous."""
        self.assertTrue(PLAN_GUIDE_PATH.is_file(), f"plan-guide not found at {PLAN_GUIDE_PATH}")
        text = PLAN_GUIDE_PATH.read_text(encoding="utf-8")
        # The skill should document recommending staged mode for rigorous depth
        self.assertTrue(
            "staged" in text.lower() and "rigorous" in text.lower(),
            "plan-guide SKILL.md must document recommending staged mode for rigorous planning depth",
        )

    def test_recommend_staged_for_six_tasks(self) -> None:
        """t-003b: plan-guide recommends staged when task count > 5.

        Boundary: 5 tasks = linear, 6 tasks = staged.
        """
        self.assertTrue(PLAN_GUIDE_PATH.is_file(), f"plan-guide not found at {PLAN_GUIDE_PATH}")
        text = PLAN_GUIDE_PATH.read_text(encoding="utf-8")
        # The skill should document a threshold for task count
        self.assertTrue(
            "staged" in text.lower(),
            "plan-guide SKILL.md must document staged mode recommendation",
        )
        # Check for a threshold mention (either >5, or a named threshold)
        self.assertTrue(
            "> 5" in text or "threshold" in text.lower(),
            "plan-guide SKILL.md must document a task-count threshold for staged mode",
        )

    def test_no_recommend_staged_for_single_stage(self) -> None:
        """t-003c: plan-guide does NOT recommend staged mode for single-stage plans (fr-14)."""
        self.assertTrue(PLAN_GUIDE_PATH.is_file(), f"plan-guide not found at {PLAN_GUIDE_PATH}")
        text = PLAN_GUIDE_PATH.read_text(encoding="utf-8")
        # The skill should document the single-stage guard
        self.assertTrue(
            "single" in text.lower() and "stage" in text.lower(),
            "plan-guide SKILL.md must document the single-stage guard (fr-14): "
            "do not recommend staged mode for single-stage plans",
        )


if __name__ == "__main__":
    unittest.main()
