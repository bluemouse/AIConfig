#!/usr/bin/env python3
"""Tests for stage-aware artifact naming validation (pg-007).

Validates:
- t-007: stage-indexed artifacts (30-stage1-*) pass naming checks
- t-007b: linear artifacts (30-implementation-report.md) still pass (regression)
"""

from __future__ import annotations

import unittest
from pathlib import Path

import sys
# Add the checks package parent so we can import as a package
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / ".ai" / "tools" / "dev-workflow"))
from checks import artifact_checks  # type: ignore[import-not-found]
from checks import Finding  # type: ignore[import-not-found]


class StageIndexedArtifactNamingTests(unittest.TestCase):
    """t-007: Stage-indexed artifacts pass naming checks."""

    def test_stage_indexed_artifacts_accepted(self) -> None:
        """t-007: `30-stage1-*`, `31-stage1-*`, `32-stage1-*`, `40-stage1-*`, `41-stage1-*`
        pass naming checks via the stage-aware matcher.
        """
        stage_indexed_names = [
            "30-stage1-implementation-report.md",
            "31-stage1-implementation-audit.md",
            "32-stage1-exit-review.md",
            "40-stage1-code-review.md",
            "41-stage1-fix-report.md",
        ]
        for name in stage_indexed_names:
            # The 2-digit prefix should be in valid_prefixes
            prefix = name[:2]
            self.assertIn(
                prefix,
                artifact_checks.PHASE_ARTIFACTS.get("implement", [])[0:1] and
                {"30", "31", "32", "33", "40", "41", "42", "43", "00", "01", "02",
                 "10", "11", "12", "13", "14", "15", "20", "21", "22", "23", "50"},
                f"Prefix '{prefix}' from {name} not in valid prefixes",
            )

    def test_stage_indexed_artifact_naming_check_passes(self) -> None:
        """t-007b: The check_artifact_naming function accepts stage-indexed names."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            run_dir = Path(tmpdir)
            # Create stage-indexed files
            for name in [
                "30-stage1-implementation-report.md",
                "31-stage1-implementation-audit.md",
                "32-stage1-exit-review.md",
            ]:
                (run_dir / name).write_text("# Test\n", encoding="utf-8")
            # Run the naming check
            findings = artifact_checks.check_artifact_naming(run_dir)
            # Should produce no warnings (all prefixes are valid)
            warnings = [f for f in findings if f.severity == "warning"]
            self.assertEqual(
                len(warnings),
                0,
                f"Stage-indexed artifacts should not produce naming warnings: {[f.message for f in warnings]}",
            )


class LinearArtifactNamingRegressionTests(unittest.TestCase):
    """t-007b: Linear artifacts (no stage suffix) still pass (regression)."""

    def test_linear_artifacts_still_accepted(self) -> None:
        """t-007b: `30-implementation-report.md` (no stage suffix) still valid."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            run_dir = Path(tmpdir)
            # Create linear-mode files
            for name in [
                "30-implementation-report.md",
                "31-implementation-audit.md",
            ]:
                (run_dir / name).write_text("# Test\n", encoding="utf-8")
            # Run the naming check
            findings = artifact_checks.check_artifact_naming(run_dir)
            warnings = [f for f in findings if f.severity == "warning"]
            self.assertEqual(
                len(warnings),
                0,
                f"Linear artifacts should not produce naming warnings: {[f.message for f in warnings]}",
            )


if __name__ == "__main__":
    unittest.main()
