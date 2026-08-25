#!/usr/bin/env python3
"""Tests for stage-exit verdict routing in verdicts.py (pg-003, t-008).

Validates:
- t-008: `plan-current` is in ACCEPT_VERDICTS and `plan-stale` is in REVISE_VERDICTS
  for the stage-exit review artifact.
"""

from __future__ import annotations

import unittest

import sys
sys.path.insert(0, ".ai/tools/dev-workflow/checks")
import verdicts  # type: ignore[import-not-found]


class StageExitVerdictRoutingTests(unittest.TestCase):
    """t-008: Stage-exit verdict routing in ACCEPT_VERDICTS and REVISE_VERDICTS."""

    def test_plan_current_accepts(self) -> None:
        """t-008a: `plan-current` is in ACCEPT_VERDICTS for stage-exit review."""
        accept = verdicts.lookup_verdicts_for_filename(
            "32-stage1-exit-review.md", verdicts.ACCEPT_VERDICTS
        )
        self.assertIn(
            "plan-current",
            accept,
            "`plan-current` must be in ACCEPT_VERDICTS for stage-exit review artifacts",
        )

    def test_plan_stale_accepts(self) -> None:
        """t-008b: `plan-stale` is in REVISE_VERDICTS for stage-exit review."""
        revise = verdicts.lookup_verdicts_for_filename(
            "32-stage1-exit-review.md", verdicts.REVISE_VERDICTS
        )
        self.assertIn(
            "plan-stale",
            revise,
            "`plan-stale` must be in REVISE_VERDICTS for stage-exit review artifacts",
        )

    def test_stage_exit_verdicts_registered(self) -> None:
        """t-008c: Both verdicts are registered in CHECKER_VERDICTS."""
        checker = verdicts.lookup_verdicts_for_filename(
            "32-stage1-exit-review.md", verdicts.CHECKER_VERDICTS
        )
        self.assertIn("plan-current", checker)
        self.assertIn("plan-stale", checker)

    def test_glob_pattern_matches_different_stage_numbers(self) -> None:
        """t-008d: Glob pattern matches stage 1, stage 2, etc."""
        for stage_num in [1, 2, 3, 10]:
            filename = f"32-stage{stage_num}-exit-review.md"
            checker = verdicts.lookup_verdicts_for_filename(
                filename, verdicts.CHECKER_VERDICTS
            )
            self.assertIn(
                "plan-current",
                checker,
                f"Glob pattern must match {filename}",
            )


if __name__ == "__main__":
    unittest.main()
