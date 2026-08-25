#!/usr/bin/env python3
"""Tests for the orchestrator staged iterator (pg-006).

Validates:
- t-006: staged mode end-to-end clean (3 stages, all pass single-pass)
- t-006b: stage failure escalates to full loop
- t-006c: plan-stale triggers re-plan
- t-006d: final deep review on cumulative range
- t-006e: linear mode unchanged (regression)
- t-006f: final review fixes are new commits

Note: These are documentation-presence tests for the orchestrator SKILL.md
and loop-contracts.md, plus structural validation of the staged-mode procedure.
Full integration tests would require a mock run directory; these tests verify
the orchestrator skill documents the staged-mode behavior.
"""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ORCHESTRATOR_PATH = REPO_ROOT / "skills" / "dev-workflow-orchestrator" / "SKILL.md"
LOOP_CONTRACTS_PATH = REPO_ROOT / "skills" / "dev-workflow-orchestrator" / "references" / "loop-contracts.md"
PERMISSION_MATRIX_PATH = REPO_ROOT / "skills" / "dev-workflow-orchestrator" / "references" / "permission-matrix.md"


class StagedOrchestratorTests(unittest.TestCase):
    """t-006 through t-006f: Orchestrator staged-mode documentation."""

    def test_staged_mode_end_to_end_clean(self) -> None:
        """t-006: orchestrator documents staged-mode end-to-end procedure."""
        text = ORCHESTRATOR_PATH.read_text(encoding="utf-8")
        self.assertIn(
            "staged",
            text.lower(),
            "Orchestrator SKILL.md must document staged mode",
        )
        # Must document the per-stage loop: implement → audit → review → commit
        self.assertTrue(
            "stage" in text.lower() and "commit" in text.lower(),
            "Orchestrator must document per-stage implement→audit→review→commit loop",
        )

    def test_staged_mode_stage_failure_escalates(self) -> None:
        """t-006b: orchestrator documents escalation to full loop on stage failure."""
        text = ORCHESTRATOR_PATH.read_text(encoding="utf-8")
        self.assertTrue(
            "escalat" in text.lower() or "full loop" in text.lower(),
            "Orchestrator must document escalation to full loop on stage failure",
        )

    def test_staged_mode_plan_stale_triggers_replan(self) -> None:
        """t-006c: orchestrator documents plan-stale triggering re-plan."""
        text = ORCHESTRATOR_PATH.read_text(encoding="utf-8")
        self.assertIn(
            "plan-stale",
            text.lower(),
            "Orchestrator must document plan-stale triggering re-plan",
        )
        self.assertIn(
            "plan-current",
            text.lower(),
            "Orchestrator must document plan-current for light refinement",
        )

    def test_final_deep_review_on_cumulative_range(self) -> None:
        """t-006d: orchestrator documents final deep review on cumulative commit range."""
        text = ORCHESTRATOR_PATH.read_text(encoding="utf-8")
        self.assertTrue(
            "final deep review" in text.lower() or "cumulative" in text.lower(),
            "Orchestrator must document final deep review on cumulative commit range",
        )

    def test_linear_mode_unchanged(self) -> None:
        """t-006e: linear mode is still documented (regression)."""
        text = ORCHESTRATOR_PATH.read_text(encoding="utf-8")
        self.assertIn(
            "linear",
            text.lower(),
            "Orchestrator must still document linear mode (regression check)",
        )

    def test_final_review_fixes_are_new_commits(self) -> None:
        """t-006f: orchestrator documents fixup commits as new commits (no amend)."""
        text = ORCHESTRATOR_PATH.read_text(encoding="utf-8")
        self.assertTrue(
            "new commit" in text.lower() or "no amend" in text.lower() or "no rebase" in text.lower(),
            "Orchestrator must document that final-review fixes are new commits (no amend/rebase)",
        )

    def test_backward_edge_independence(self) -> None:
        """t-006g: orchestrator documents backward-edge independence from stage-exit review."""
        text = ORCHESTRATOR_PATH.read_text(encoding="utf-8")
        self.assertTrue(
            "independent" in text.lower() or "orthogonal" in text.lower(),
            "Orchestrator must document that in-stage backward edges are independent from stage-exit review",
        )


class StagedLoopContractsTests(unittest.TestCase):
    """Loop 5 (Stage-exit) and Loop 6 (Final deep review) contracts."""

    def test_loop_5_stage_exit_contract_exists(self) -> None:
        """Loop 5 (Stage-exit) contract is documented."""
        text = LOOP_CONTRACTS_PATH.read_text(encoding="utf-8")
        self.assertIn(
            "Loop 5",
            text,
            "loop-contracts.md must document Loop 5 (Stage-exit)",
        )
        self.assertIn(
            "plan-current",
            text,
            "Loop 5 contract must mention plan-current verdict",
        )

    def test_loop_6_final_deep_review_contract_exists(self) -> None:
        """Loop 6 (Final deep review) contract is documented."""
        text = LOOP_CONTRACTS_PATH.read_text(encoding="utf-8")
        self.assertIn(
            "Loop 6",
            text,
            "loop-contracts.md must document Loop 6 (Final deep review)",
        )


class StagedPermissionMatrixTests(unittest.TestCase):
    """Permission matrix staged-mode extension."""

    def test_permission_matrix_documents_per_stage_commit(self) -> None:
        """Permission matrix documents per-stage commit in staged mode."""
        text = PERMISSION_MATRIX_PATH.read_text(encoding="utf-8")
        self.assertTrue(
            "per-stage" in text.lower() or "staged-mode" in text.lower(),
            "Permission matrix must document per-stage commit or staged-mode commit "
            "(using 'per-stage commit' or 'staged-mode commit' to avoid collision with git 'staged')",
        )


if __name__ == "__main__":
    unittest.main()
