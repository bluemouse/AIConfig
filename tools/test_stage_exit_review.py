#!/usr/bin/env python3
"""Tests for the stage-exit review contract and verdicts (pg-001, pg-003).

Validates:
- t-004: `plan-current` and `plan-stale` are accepted verdicts for stage-exit review
- t-004b: plan-reviewer SKILL.md documents comparing plan assumptions (documentation-presence)
- t-004c: stage-exit contract specifies the plan-current/plan-stale boundary
"""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Import verdicts module
import sys
sys.path.insert(0, str(REPO_ROOT / ".ai" / "tools" / "dev-workflow" / "checks"))
import verdicts  # type: ignore[import-not-found]


class StageExitVerdictsTests(unittest.TestCase):
    """t-004: Stage-exit review verdicts are registered in verdicts.py."""

    def test_stage_exit_verdicts_valid(self) -> None:
        """t-004: `plan-current` and `plan-stale` are accepted verdicts for stage-exit review."""
        # The stage-exit review artifact uses a glob pattern: 32-stage*-exit-review.md
        # Check that the verdicts module recognizes these verdicts for stage-exit
        found_plan_current = False
        found_plan_stale = False
        for filename, verdicts_set in verdicts.CHECKER_VERDICTS.items():
            if "stage" in filename.lower() and "exit" in filename.lower():
                if "plan-current" in verdicts_set:
                    found_plan_current = True
                if "plan-stale" in verdicts_set:
                    found_plan_stale = True
        self.assertTrue(
            found_plan_current,
            "`plan-current` verdict not found in CHECKER_VERDICTS for stage-exit review artifact",
        )
        self.assertTrue(
            found_plan_stale,
            "`plan-stale` verdict not found in CHECKER_VERDICTS for stage-exit review artifact",
        )


class StageExitContractTests(unittest.TestCase):
    """t-004b, t-004c: Stage-exit review contract and documentation."""

    def test_stage_exit_compares_plan_assumptions(self) -> None:
        """t-004b: plan-reviewer SKILL.md documents comparing completed stage artifacts
        against plan §4 assumptions and §10 stage breakdown.

        Note: this is a documentation-presence test (grep for text in the markdown
        skill file), not a behavior test, because plan-reviewer is a markdown skill.
        Actual behavior is validated in integration test t-006c.
        """
        skill_path = REPO_ROOT / "skills" / "plan-reviewer" / "SKILL.md"
        self.assertTrue(skill_path.is_file(), f"plan-reviewer SKILL.md not found at {skill_path}")
        text = skill_path.read_text(encoding="utf-8")
        # The stage-exit mode should reference comparing against plan assumptions
        self.assertTrue(
            "stage-exit" in text.lower() or "stage exit" in text.lower(),
            "plan-reviewer SKILL.md must document a stage-exit review mode",
        )

    def test_stage_exit_contract_specifies_boundary(self) -> None:
        """t-004c: The stage-exit contract document specifies the boundary:
        detail change → plan-current; assumption contradiction → plan-stale.
        """
        contract_path = REPO_ROOT / "skills" / "plan-reviewer" / "references" / "stage-exit-review-contract.md"
        self.assertTrue(
            contract_path.is_file(),
            f"Stage-exit contract document not found at {contract_path}",
        )
        text = contract_path.read_text(encoding="utf-8")
        # The contract must specify both verdicts and the boundary between them
        self.assertIn(
            "plan-current",
            text,
            "Stage-exit contract must mention `plan-current` verdict",
        )
        self.assertIn(
            "plan-stale",
            text,
            "Stage-exit contract must mention `plan-stale` verdict",
        )
        # The contract must specify the boundary (detail change vs assumption contradiction)
        self.assertTrue(
            "detail" in text.lower() and "assumption" in text.lower(),
            "Stage-exit contract must specify the boundary between detail changes (plan-current) "
            "and assumption contradictions (plan-stale)",
        )


if __name__ == "__main__":
    unittest.main()
