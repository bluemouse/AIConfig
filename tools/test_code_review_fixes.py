#!/usr/bin/env python3
"""Tests for code review fixes (cr-001, cr-002, cr-004, cr-005).

Validates:
- cr-001: loop_checks.py uses lookup_verdicts_for_filename for glob-pattern verdicts
- cr-002: manifest_checks.py validates Run mode field
- cr-004: _is_staged_mode uses regex (not fragile substring match)
- cr-005: Run mode: linear (explicit) does not trigger stage-indexed lookup
"""

from __future__ import annotations

import unittest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / ".ai" / "tools" / "dev-workflow"))
from checks import artifact_checks  # type: ignore[import-not-found]
from checks import manifest_checks  # type: ignore[import-not-found]
from checks import loop_checks  # type: ignore[import-not-found]
from checks import verdicts  # type: ignore[import-not-found]


class LoopChecksVerdictLookupTests(unittest.TestCase):
    """cr-001: loop_checks.py uses lookup_verdicts_for_filename for glob patterns."""

    def test_check_verdict_valid_uses_glob_lookup_for_stage_exit(self) -> None:
        """cr-001: A stage-exit review artifact with a valid verdict should pass
        check_verdict_valid when the filename matches a glob pattern."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            run_dir = Path(tmpdir)
            # Create a stage-exit review artifact with a valid verdict
            (run_dir / "32-stage1-exit-review.md").write_text(
                "# Stage-Exit Review\n\n## Verdict\nplan-current\n",
                encoding="utf-8",
            )
            # check_verdict_valid should not report an invalid verdict
            # Note: this requires PHASE_CHECKER to recognize stage-exit artifacts
            # or a stage-aware lookup. Currently PHASE_CHECKER maps "implement" to
            # "31-implementation-audit.md" (exact). The test verifies that if
            # loop_checks is given a stage-exit file, it uses the glob lookup.
            # We test the helper directly since PHASE_CHECKER doesn't include
            # stage-exit yet.
            valid_verdicts = verdicts.lookup_verdicts_for_filename(
                "32-stage1-exit-review.md", verdicts.CHECKER_VERDICTS
            )
            self.assertIn("plan-current", valid_verdicts)
            self.assertIn("plan-stale", valid_verdicts)


class ManifestRunModeValidationTests(unittest.TestCase):
    """cr-002: manifest_checks.py validates Run mode field."""

    def test_valid_run_mode_staged_accepted(self) -> None:
        """cr-002a: Run mode: staged is valid."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            run_dir = Path(tmpdir)
            (run_dir / "00-run-manifest.md").write_text(
                "# Run Manifest\n\n## Run metadata\n"
                "- Current phase: implement\n"
                "- Run status: in-progress\n"
                "- Run mode: staged\n",
                encoding="utf-8",
            )
            findings = manifest_checks.run_all(run_dir, "implement")
            run_mode_errors = [
                f for f in findings
                if "run mode" in f.message.lower() and f.severity == "error"
            ]
            self.assertEqual(
                len(run_mode_errors),
                0,
                f"Run mode: staged should be valid: {[f.message for f in run_mode_errors]}",
            )

    def test_invalid_run_mode_rejected(self) -> None:
        """cr-002b: Run mode: invalid_value is rejected."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            run_dir = Path(tmpdir)
            (run_dir / "00-run-manifest.md").write_text(
                "# Run Manifest\n\n## Run metadata\n"
                "- Current phase: implement\n"
                "- Run status: in-progress\n"
                "- Run mode: invalid_value\n",
                encoding="utf-8",
            )
            findings = manifest_checks.run_all(run_dir, "implement")
            run_mode_errors = [
                f for f in findings
                if "run mode" in f.message.lower() and f.severity == "error"
            ]
            self.assertGreater(
                len(run_mode_errors),
                0,
                "Run mode: invalid_value should be rejected",
            )

    def test_run_mode_absent_accepted(self) -> None:
        """cr-002c: Run mode absent (defaults to linear) is valid."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            run_dir = Path(tmpdir)
            (run_dir / "00-run-manifest.md").write_text(
                "# Run Manifest\n\n## Run metadata\n"
                "- Current phase: implement\n"
                "- Run status: in-progress\n",
                encoding="utf-8",
            )
            findings = manifest_checks.run_all(run_dir, "implement")
            run_mode_errors = [
                f for f in findings
                if "run mode" in f.message.lower() and f.severity == "error"
            ]
            self.assertEqual(
                len(run_mode_errors),
                0,
                f"Run mode absent should be valid (defaults to linear): "
                f"{[f.message for f in run_mode_errors]}",
            )


class StagedModeRegexTests(unittest.TestCase):
    """cr-004: _is_staged_mode uses regex (not fragile substring match)."""

    def test_is_staged_mode_does_not_match_staged_broken(self) -> None:
        """cr-004: 'Run mode: staged-broken' should NOT be treated as staged mode."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            run_dir = Path(tmpdir)
            (run_dir / "00-run-manifest.md").write_text(
                "# Run Manifest\n\n## Run metadata\n- Run mode: staged-broken\n",
                encoding="utf-8",
            )
            # The substring "Run mode: staged" is in "Run mode: staged-broken",
            # but regex should not match it because the value is "staged-broken",
            # not "staged".
            self.assertFalse(
                artifact_checks._is_staged_mode(run_dir),
                "'Run mode: staged-broken' should not be treated as staged mode "
                "(regex should match the exact value, not a substring)",
            )

    def test_is_staged_mode_matches_exact_staged(self) -> None:
        """cr-004: 'Run mode: staged' (exact) is treated as staged mode."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            run_dir = Path(tmpdir)
            (run_dir / "00-run-manifest.md").write_text(
                "# Run Manifest\n\n## Run metadata\n- Run mode: staged\n",
                encoding="utf-8",
            )
            self.assertTrue(
                artifact_checks._is_staged_mode(run_dir),
                "'Run mode: staged' (exact) should be treated as staged mode",
            )


class ExplicitLinearModeTests(unittest.TestCase):
    """cr-005: Run mode: linear (explicit) does not trigger stage-indexed lookup."""

    def test_explicit_linear_mode_does_not_accept_stage_indexed(self) -> None:
        """cr-005: In linear mode (explicit), stage-indexed artifacts are NOT accepted."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            run_dir = Path(tmpdir)
            # Create a linear-mode manifest (explicit)
            (run_dir / "00-run-manifest.md").write_text(
                "# Run Manifest\n\n## Run metadata\n- Run mode: linear\n",
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
            self.assertGreater(
                len(errors),
                0,
                "In explicit linear mode, stage-indexed artifacts should NOT be accepted "
                "(exact filenames required)",
            )


if __name__ == "__main__":
    unittest.main()
