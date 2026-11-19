#!/usr/bin/env python3
"""Tests for the stage-aware PHASE_ARTIFACTS matcher (audit defect fix).

Validates that check_artifacts_exist and check_artifact_sections accept
stage-indexed variants (e.g., 30-stage1-implementation-report.md) in staged
mode, while preserving exact-filename lookup in linear mode.

This test exposes the defect found in the implementation audit:
PHASE_ARTIFACTS uses exact filenames, so stage-indexed variants are not
recognized as the required implement artifact.
"""

from __future__ import annotations

import unittest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / ".agents" / "tools" / "dev-workflow"))
from checks import artifact_checks  # type: ignore[import-not-found]
from checks import Finding  # type: ignore[import-not-found]


class StageAwareArtifactMatcherTests(unittest.TestCase):
    """Tests that check_artifacts_exist accepts stage-indexed variants in staged mode."""

    def test_stage_indexed_artifact_recognized_in_staged_mode(self) -> None:
        """In staged mode, 30-stage1-implementation-report.md satisfies the
        30-implementation-report.md requirement — no 'missing artifact' error."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            run_dir = Path(tmpdir)
            # Create a staged-mode manifest
            (run_dir / "00-run-manifest.md").write_text(
                "# Run Manifest\n\n## Run metadata\n- Run mode: staged\n",
                encoding="utf-8",
            )
            # Create stage-indexed artifacts (not the exact linear filename)
            (run_dir / "30-stage1-implementation-report.md").write_text(
                "# Implementation Report\n", encoding="utf-8"
            )
            (run_dir / "31-stage1-implementation-audit.md").write_text(
                "## Verdict\npass\n", encoding="utf-8"
            )
            # Run check_artifacts_exist for the implement phase
            findings = artifact_checks.check_artifacts_exist(run_dir, "implement")
            errors = [f for f in findings if f.severity == "error"]
            self.assertEqual(
                len(errors),
                0,
                f"Stage-indexed artifacts should be recognized in staged mode: "
                f"{[f.message for f in errors]}",
            )

    def test_linear_artifact_still_recognized_in_linear_mode(self) -> None:
        """In linear mode, 30-implementation-report.md (exact filename) is required."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            run_dir = Path(tmpdir)
            # Create a linear-mode manifest (no Run mode field = linear default)
            (run_dir / "00-run-manifest.md").write_text(
                "# Run Manifest\n\n## Run metadata\n",
                encoding="utf-8",
            )
            # Create the exact linear filename
            (run_dir / "30-implementation-report.md").write_text(
                "# Implementation Report\n", encoding="utf-8"
            )
            (run_dir / "31-implementation-audit.md").write_text(
                "## Verdict\npass\n", encoding="utf-8"
            )
            # Run check_artifacts_exist for the implement phase
            findings = artifact_checks.check_artifacts_exist(run_dir, "implement")
            errors = [f for f in findings if f.severity == "error"]
            self.assertEqual(
                len(errors),
                0,
                f"Linear artifacts should be recognized in linear mode: "
                f"{[f.message for f in errors]}",
            )

    def test_stage_indexed_artifact_sections_checked_in_staged_mode(self) -> None:
        """In staged mode, check_artifact_sections validates stage-indexed variants."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            run_dir = Path(tmpdir)
            # Create a staged-mode manifest
            (run_dir / "00-run-manifest.md").write_text(
                "# Run Manifest\n\n## Run metadata\n- Run mode: staged\n",
                encoding="utf-8",
            )
            # Create stage-indexed artifact WITH required sections
            (run_dir / "30-stage1-implementation-report.md").write_text(
                "# Implementation Report\n", encoding="utf-8"
            )
            (run_dir / "31-stage1-implementation-audit.md").write_text(
                "## Verdict\npass\n", encoding="utf-8"
            )
            # Run check_artifact_sections for the implement phase
            findings = artifact_checks.check_artifact_sections(run_dir, "implement")
            errors = [f for f in findings if f.severity == "error"]
            self.assertEqual(
                len(errors),
                0,
                f"Stage-indexed artifact sections should be validated without errors: "
                f"{[f.message for f in errors]}",
            )

    def test_stage_indexed_artifact_missing_section_reported(self) -> None:
        """In staged mode, a stage-indexed artifact missing a required section is reported."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            run_dir = Path(tmpdir)
            # Create a staged-mode manifest
            (run_dir / "00-run-manifest.md").write_text(
                "# Run Manifest\n\n## Run metadata\n- Run mode: staged\n",
                encoding="utf-8",
            )
            # Create stage-indexed audit artifact WITHOUT the required ## Verdict section
            (run_dir / "30-stage1-implementation-report.md").write_text(
                "# Implementation Report\n", encoding="utf-8"
            )
            (run_dir / "31-stage1-implementation-audit.md").write_text(
                "# Audit Report\n(no verdict)\n", encoding="utf-8"
            )
            # Run check_artifact_sections for the implement phase
            findings = artifact_checks.check_artifact_sections(run_dir, "implement")
            errors = [f for f in findings if f.severity == "error"]
            self.assertGreater(
                len(errors),
                0,
                "Missing ## Verdict section in stage-indexed audit should be reported",
            )


if __name__ == "__main__":
    unittest.main()


class StageScopingRegressionTest(unittest.TestCase):
    """Regression tests for stage-scoped artifact resolution.

    Unscoped resolution must be deterministic (highest stage index wins,
    not first filesystem match) and --stage N must never resolve stage M
    artifacts. Root cause: first-match resolution let a malformed stage-2
    artifact pass validation against stage-1's file.
    """

    @staticmethod
    def _make_staged_run(tmpdir: str) -> Path:
        run_dir = Path(tmpdir)
        (run_dir / "00-run-manifest.md").write_text(
            "# Run Manifest\n\n## Run metadata\n- Run mode: staged\n",
            encoding="utf-8",
        )
        return run_dir

    def test_unscoped_resolves_highest_stage(self) -> None:
        """Without --stage, the highest stage index must win regardless of
        directory iteration order."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            run_dir = self._make_staged_run(tmpdir)
            (run_dir / "30-stage1-implementation-report.md").write_text(
                "# Implementation Report\n", encoding="utf-8"
            )
            (run_dir / "30-stage2-implementation-report.md").write_text(
                "# Implementation Report\n", encoding="utf-8"
            )
            path = artifact_checks._find_stage_indexed_artifact(
                run_dir, "30-implementation-report.md", "implement"
            )
            self.assertIsNotNone(path)
            self.assertEqual(path.name, "30-stage2-implementation-report.md")

    def test_stage_scope_excludes_other_stages(self) -> None:
        """--stage 1 must not resolve a stage-2 artifact."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            run_dir = self._make_staged_run(tmpdir)
            (run_dir / "30-stage2-implementation-report.md").write_text(
                "# Implementation Report\n", encoding="utf-8"
            )
            path = artifact_checks._find_stage_indexed_artifact(
                run_dir, "30-implementation-report.md", "implement", stage=1
            )
            self.assertIsNone(path)

    def test_stage_scope_finds_own_stage(self) -> None:
        """--stage 2 must resolve the stage-2 artifact even when stage 1 exists."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            run_dir = self._make_staged_run(tmpdir)
            (run_dir / "30-stage1-implementation-report.md").write_text(
                "# Implementation Report\n", encoding="utf-8"
            )
            (run_dir / "30-stage2-implementation-report.md").write_text(
                "# Implementation Report\n", encoding="utf-8"
            )
            path = artifact_checks._find_stage_indexed_artifact(
                run_dir, "30-implementation-report.md", "implement", stage=2
            )
            self.assertIsNotNone(path)
            self.assertEqual(path.name, "30-stage2-implementation-report.md")

    def test_stage_scoped_existence_check_fails_on_wrong_stage(self) -> None:
        """check_artifacts_exist(stage=1) must error when only stage-2 exists."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            run_dir = self._make_staged_run(tmpdir)
            (run_dir / "30-stage2-implementation-report.md").write_text(
                "# Implementation Report\n", encoding="utf-8"
            )
            (run_dir / "31-stage2-implementation-audit.md").write_text(
                "## Verdict\npass\n", encoding="utf-8"
            )
            findings = artifact_checks.check_artifacts_exist(
                run_dir, "implement", stage=1
            )
            errors = [f for f in findings if f.severity == "error"]
            self.assertTrue(
                errors, "stage-1 validation must not pass against stage-2 artifacts"
            )
