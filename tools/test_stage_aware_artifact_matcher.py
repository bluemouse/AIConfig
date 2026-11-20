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

import os
import sys
HARNESS_DIR = Path(__file__).resolve().parent.parent / "skills" / "dev-workflow-orchestrator" / "scripts"
sys.path.insert(0, str(HARNESS_DIR))
for _mod_name in [
    k for k in list(sys.modules)
    if k in {"checks", "validate_phase"} or k.startswith("checks.")
]:
    _mod_file = getattr(sys.modules[_mod_name], "__file__", "") or ""
    if str(HARNESS_DIR) not in _mod_file:
        del sys.modules[_mod_name]

from checks import artifact_checks  # type: ignore[import-not-found]
from checks import Finding  # type: ignore[import-not-found]
import validate_phase  # type: ignore[import-not-found]


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


class StageScopedPhaseValidationTests(unittest.TestCase):
    """End-to-end and CLI stage-scoping tests for validate_phase (cr-006)."""

    @staticmethod
    def _make_full_staged_manifest(
        run_dir: Path, phase: str = "implement", phase_heading: str = "### Phase 3: Implement"
    ) -> None:
        (run_dir / "00-run-manifest.md").write_text(
            "# Run Manifest\n\n"
            "## Run metadata\n"
            f"- Current phase: {phase}\n"
            "- Run status: in-progress\n"
            "- Run mode: staged\n\n"
            "## Phase status\n"
            f"{phase_heading}\n"
            "- Status: in-progress\n"
            "- Backward edges received: 0\n\n"
            "## Artifact registry\n"
            "| Artifact | Path | Phase | Status |\n"
            "|----------|------|-------|--------|\n",
            encoding="utf-8",
        )

    def test_validate_phase_stage_arg_scopes_loop_and_handoff_checks(self) -> None:
        """cr-006(a): run_phase_validation(..., stage=1) returns [] when stage 1 is
        valid even if stage 2 has inverted mtimes, a finding missing
        root-cause-phase, invalid verdict, loop-cap excess, missing
        '## Files changed', and 40-final-deep-review-r4.md exists on disk."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            run_dir = Path(tmpdir)
            self._make_full_staged_manifest(run_dir)
            s1_report = run_dir / "30-stage1-implementation-report.md"
            s1_audit = run_dir / "31-stage1-implementation-audit.md"
            s1_report.write_text(
                "# Implementation Report\n\n## Files changed\n- foo.py\n",
                encoding="utf-8",
            )
            os.utime(s1_report, ns=(1_000_000_000, 1_000_000_000))
            s1_audit.write_text("## Verdict\npass\n", encoding="utf-8")
            os.utime(s1_audit, ns=(2_000_000_000, 2_000_000_000))

            # Broken stage-2 artifacts + non-stage-indexed final review round file.
            s2_report = run_dir / "30-stage2-implementation-report.md"
            s2_audit = run_dir / "31-stage2-implementation-audit.md"
            s2_r4 = run_dir / "31-stage2-implementation-audit-r4.md"
            final_r4 = run_dir / "40-final-deep-review-r4.md"
            s2_audit.write_text(
                "## Verdict\nbogus\n\n#### ia-001: defect\n- Issue: broken\n",
                encoding="utf-8",
            )
            os.utime(s2_audit, ns=(3_000_000_000, 3_000_000_000))
            s2_report.write_text("# Implementation Report\n", encoding="utf-8")
            os.utime(s2_report, ns=(4_000_000_000, 4_000_000_000))
            s2_r4.write_text("## Verdict\nfail\n", encoding="utf-8")
            final_r4.write_text("# Code Review Report\n\n## Verdict\nneeds revision\n", encoding="utf-8")

            findings = validate_phase.run_phase_validation(
                run_dir, "implement", stage=1
            )
            self.assertEqual(
                findings,
                [],
                f"stage=1 validation should return [] despite broken stage 2 and "
                f"non-stage-indexed -r4 artifact: {[f.message for f in findings]}",
            )

    def test_validate_phase_stage_arg_flags_invalid_stage1_when_stage2_valid(self) -> None:
        """cr-006(b): run_phase_validation(..., stage=1) flags stage-1 inverted
        mtimes, missing root-cause-phase, invalid verdict, loop cap, and
        handoff errors (naming 31-stage1-implementation-audit.md) even when
        stage 2 is clean."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            run_dir = Path(tmpdir)
            self._make_full_staged_manifest(run_dir)
            s1_report = run_dir / "30-stage1-implementation-report.md"
            s1_audit = run_dir / "31-stage1-implementation-audit.md"
            s1_r4 = run_dir / "31-stage1-implementation-audit-r4.md"
            s1_audit.write_text(
                "## Verdict\nbogus\n\n#### ia-001: defect\n- Issue: missing root cause\n",
                encoding="utf-8",
            )
            os.utime(s1_audit, ns=(1_000_000_000, 1_000_000_000))
            s1_report.write_text("# Implementation Report\n", encoding="utf-8")
            os.utime(s1_report, ns=(2_000_000_000, 2_000_000_000))
            s1_r4.write_text("## Verdict\nfail\n", encoding="utf-8")

            # Clean stage 2 must not mask stage 1's failures when stage=1.
            s2_report = run_dir / "30-stage2-implementation-report.md"
            s2_audit = run_dir / "31-stage2-implementation-audit.md"
            s2_report.write_text(
                "# Implementation Report\n\n## Files changed\n- foo.py\n",
                encoding="utf-8",
            )
            os.utime(s2_report, ns=(3_000_000_000, 3_000_000_000))
            s2_audit.write_text("## Verdict\npass\n", encoding="utf-8")
            os.utime(s2_audit, ns=(4_000_000_000, 4_000_000_000))

            findings = validate_phase.run_phase_validation(
                run_dir, "implement", stage=1
            )
            error_messages = [f.message for f in findings if f.severity == "error"]
            self.assertTrue(
                any(
                    "Invalid verdict" in m and "31-stage1-implementation-audit.md" in m
                    for m in error_messages
                ),
                f"Expected stage-1 invalid verdict error naming stage1 file: {error_messages}",
            )
            self.assertTrue(
                any(
                    "predates its doer" in m and "31-stage1-implementation-audit.md" in m
                    for m in error_messages
                ),
                f"Expected stage-1 inverted mtime error naming stage1 file: {error_messages}",
            )
            self.assertTrue(
                any(
                    "root-cause-phase" in m and "31-stage1-implementation-audit.md" in m
                    for m in error_messages
                ),
                f"Expected stage-1 missing root-cause-phase error naming stage1 file: {error_messages}",
            )
            self.assertTrue(
                any("Loop cap exceeded" in m for m in error_messages),
                f"Expected stage-1 loop cap error: {error_messages}",
            )
            self.assertTrue(
                any("## Files changed" in m for m in error_messages),
                f"Expected stage-1 handoff consumer-ready error: {error_messages}",
            )

    def test_code_review_stage2_clean_ignores_stage1_needs_revision(self) -> None:
        """cr-006(c): `--phase code-review --stage 2` passes cleanly without
        41-stage2-fix-report.md even when 40-stage1-code-review.md (and
        40-final-deep-review.md) have `needs revision`."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            run_dir = Path(tmpdir)
            self._make_full_staged_manifest(
                run_dir, phase="code-review", phase_heading="### Phase 4: Code Review"
            )
            (run_dir / "40-stage1-code-review.md").write_text(
                "# Code Review Report\n\n## Verdict\nneeds revision\n\n"
                "#### cr-001: bug\n- root-cause-phase: local\n",
                encoding="utf-8",
            )
            (run_dir / "40-final-deep-review.md").write_text(
                "# Code Review Report\n\n## Verdict\nneeds revision\n\n"
                "#### cr-002: bug\n- root-cause-phase: local\n",
                encoding="utf-8",
            )
            (run_dir / "40-stage2-code-review.md").write_text(
                "# Code Review Report\n\n## Verdict\nready to commit\n",
                encoding="utf-8",
            )

            findings = validate_phase.run_phase_validation(
                run_dir, "code-review", stage=2
            )
            errors = [f for f in findings if f.severity == "error"]
            self.assertEqual(
                errors,
                [],
                f"Clean stage 2 code-review should not require 41-stage2-fix-report.md "
                f"or be shadowed by stage 1 / final review: {[f.message for f in errors]}",
            )

    def test_validate_phase_cli_stage_flag_subprocess(self) -> None:
        """cr-006(d): invoking `validate_phase.py --phase implement --run-dir ... --stage 1`
        via subprocess succeeds while `--stage 2` fails on broken stage 2."""
        import subprocess
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            run_dir = Path(tmpdir)
            self._make_full_staged_manifest(run_dir)
            s1_report = run_dir / "30-stage1-implementation-report.md"
            s1_audit = run_dir / "31-stage1-implementation-audit.md"
            s1_report.write_text(
                "# Implementation Report\n\n## Files changed\n- foo.py\n",
                encoding="utf-8",
            )
            os.utime(s1_report, ns=(1_000_000_000, 1_000_000_000))
            s1_audit.write_text("## Verdict\npass\n", encoding="utf-8")
            os.utime(s1_audit, ns=(2_000_000_000, 2_000_000_000))

            s2_report = run_dir / "30-stage2-implementation-report.md"
            s2_audit = run_dir / "31-stage2-implementation-audit.md"
            s2_report.write_text("# Implementation Report\n", encoding="utf-8")
            os.utime(s2_report, ns=(4_000_000_000, 4_000_000_000))
            s2_audit.write_text("## Verdict\nbogus\n", encoding="utf-8")
            os.utime(s2_audit, ns=(3_000_000_000, 3_000_000_000))

            script = HARNESS_DIR / "validate_phase.py"
            res_s1 = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--phase",
                    "implement",
                    "--run-dir",
                    str(run_dir),
                    "--stage",
                    "1",
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(
                res_s1.returncode,
                0,
                f"CLI --stage 1 should pass: {res_s1.stdout}\n{res_s1.stderr}",
            )
            self.assertIn("PHASE VALIDATION PASSED", res_s1.stdout)

            res_s2 = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--phase",
                    "implement",
                    "--run-dir",
                    str(run_dir),
                    "--stage",
                    "2",
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(res_s2.returncode, 1)
            self.assertIn("PHASE VALIDATION FAILED", res_s2.stdout)


if __name__ == "__main__":
    unittest.main()
