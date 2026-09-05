#!/usr/bin/env python3
"""Tests for the dev-workflow harness defect fixes.

Each test verifies a specific defect fix by creating a temporary run directory
with a known artifact configuration and asserting the validation result.

Defect id series — two review rounds, ids overlap between rounds:
- ``dw-NNN``: harness defect round (validator/template divergences).
- ``cr-001``..``cr-006`` (round 1): findings on the original defect fixes.
- ``cr-007``..``cr-012`` (round 2): regression tests for round-2 findings;
  the ``fixes round-2 cr-NNN`` notes reference round-2 finding ids. Round-2
  cr-006/cr-007 were resolved as this docstring's accuracy and an assertion
  inside ``BackwardEdgeCountTests.test_code_review_phase_parsed``.

Covers:
- dw-001: verdict extraction tolerates template heading/line forms
- dw-002: clean first-pass code review does not require a fix report
- dw-003: backward-edge manifest integrity check (disk parsing + section parsing)
- dw-004: backward-packet finding-id validation reads Source artifact field
- dw-005: staged-mode awareness in loop_checks, handoff_checks, check_pre_phase
- dw-006: staged-mode commit permission for implement/code-review phases
- dw-008: code-review loop end-state mtime semantics
- cr-001: converged multi-round code-review loops pass mtime validation
- cr-002: accepted reviews with minor findings need no fix report
- cr-003: staged-mode mtime check compares same-stage pairs only
- cr-006: linear-mode commit blocking verified against a real git repo
- cr-007: staged-mode final deep review / final fix report recognized (fixes round-2 cr-001/cr-002)
- cr-008: per-stage reviews explicitly inspected for findings (fixes round-2 cr-003)
- cr-009: ``- Overall verdict:`` list-item form matched (fixes round-2 cr-004)
- cr-010: verdict matching uses match_verdict, not substring (fixes round-2 cr-005)
- cr-011: orphan disk packets for un-manifested phases flagged (fixes round-2 cr-008)
- cr-012: backward packet resolves stage-indexed source artifact (fixes round-2 cr-009)

Not covered here — documentation fixes with no dedicated tests (landed as prose
in COMMAND.md / SKILL.md / manifest-format.md / dev-workflow.md):
- dw-007 (COMMAND.md 6-phase rewording), dw-009 (``-r<N>`` round-artifact copy
  naming), dw-010 (manifest ``clarify`` phase enum), dw-011 (staged
  ``validate_phase`` insertion), dw-012 (dev-workflow.md harness section).
  dw-013 (test gaps) is addressed by this suite itself.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# Allow importing checks/ whether run as a script or module.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / ".ai" / "tools" / "dev-workflow"))

from checks import artifact_checks  # type: ignore[import-not-found]
from checks import handoff_checks  # type: ignore[import-not-found]
from checks import loop_checks  # type: ignore[import-not-found]
from checks import manifest_checks  # type: ignore[import-not-found]
from checks import mode_checks  # type: ignore[import-not-found]
from checks import verdicts  # type: ignore[import-not-found]
import check_pre_phase  # type: ignore[import-not-found]


def _make_run_dir(tmpdir: str, manifest: str = "# Run Manifest\n\n## Run metadata\n- Run mode: linear\n") -> Path:
    """Create a run directory with a manifest."""
    run_dir = Path(tmpdir)
    (run_dir / "00-run-manifest.md").write_text(manifest, encoding="utf-8")
    return run_dir


# Monotonic mtime counter for deterministic file ordering. Explicit os.utime
# timestamps are portable across filesystems (no reliance on timestamp
# granularity), unlike sleep-based ordering which can yield equal mtimes on
# coarse-grained filesystems (e.g. 1s granularity).
_mtime_counter = 1_000_000_000_000_000_000  # 2001-09-09T01:46:40Z, in ns


def _set_mtime(path: Path) -> None:
    """Set a file's mtime to a fresh, strictly increasing timestamp (ns)."""
    global _mtime_counter
    _mtime_counter += 1_000_000  # +1ms per call
    os.utime(path, ns=(_mtime_counter, _mtime_counter))


class VerdictExtractionTests(unittest.TestCase):
    """dw-001: extract_verdict tolerates template heading/line forms."""

    def test_numbered_verdict_heading(self) -> None:
        """## 1. Verdict heading (research-reviewer/plan-reviewer template)."""
        text = "## 1. Verdict\n- Verdict: ready\n"
        self.assertEqual(verdicts.extract_verdict(text), "ready")

    def test_overall_verdict_heading(self) -> None:
        """## 8. Overall verdict heading (code-reviewer template)."""
        text = "## 8. Overall verdict\n\n- Loop verdict: ready to commit\n"
        self.assertEqual(verdicts.extract_verdict(text), "ready to commit")

    def test_plain_verdict_heading(self) -> None:
        """## Verdict heading (implementation-auditor template)."""
        text = "## Verdict\n\npass — all covered\n"
        self.assertEqual(verdicts.extract_verdict(text), "pass — all covered")

    def test_loop_verdict_heading(self) -> None:
        """## Loop verdict heading."""
        text = "## Loop verdict\n\nneeds revision\n"
        self.assertEqual(verdicts.extract_verdict(text), "needs revision")

    def test_no_verdict_heading_returns_none(self) -> None:
        """No verdict heading → None."""
        self.assertIsNone(verdicts.extract_verdict("# Report\n\nNo verdict here.\n"))


class CleanCodeReviewTests(unittest.TestCase):
    """dw-002: clean first-pass code review does not require a fix report."""

    def test_clean_review_no_fix_report_required(self) -> None:
        """A ready-to-commit review with no findings needs no 41-fix-report.md."""
        with tempfile.TemporaryDirectory() as tmpdir:
            run_dir = _make_run_dir(tmpdir)
            (run_dir / "40-code-review.md").write_text(
                "# Code Review Report\n\n## Verdict\nready to commit\n\nNo findings.\n",
                encoding="utf-8",
            )
            findings = artifact_checks.run_all(run_dir, "code-review")
            errors = [f for f in findings if f.severity == "error"]
            self.assertEqual(
                len(errors), 0,
                f"Clean review should not require fix report: {[f.message for f in errors]}",
            )

    def test_review_with_findings_requires_fix_report(self) -> None:
        """A needs-revision review with findings requires 41-fix-report.md."""
        with tempfile.TemporaryDirectory() as tmpdir:
            run_dir = _make_run_dir(tmpdir)
            (run_dir / "40-code-review.md").write_text(
                "# Code Review Report\n\n## Verdict\nneeds revision\n\ncr-001: bug\n",
                encoding="utf-8",
            )
            findings = artifact_checks.run_all(run_dir, "code-review")
            errors = [f for f in findings if f.severity == "error"]
            self.assertTrue(
                any("41-fix-report.md" in f.message for f in errors),
                f"Review with findings should require fix report: {[f.message for f in errors]}",
            )


class BackwardEdgeCountTests(unittest.TestCase):
    """dw-003: backward-edge manifest integrity check."""

    MANIFEST = """# Run Manifest

## Run metadata
- Current phase: plan
- Run status: in-progress

## Phase status

### Phase 0: Clarify
- Status: accepted
- Backward edges received: 0

### Phase 1: Research
- Status: accepted
- Backward edges received: 0

### Phase 2: Plan
- Status: backward-edge-received
- Backward edges received: 1

### Phase 3: Implement
- Status: not-started
- Backward edges received: 0

### Phase 4: Code Review
- Status: not-started
- Backward edges received: 0

## Artifact registry
| Artifact | Path | Phase | Status |
|----------|------|-------|--------|
"""

    def test_matching_counts_pass(self) -> None:
        """Manifest count matches disk count → no findings."""
        with tempfile.TemporaryDirectory() as tmpdir:
            run_dir = _make_run_dir(tmpdir, self.MANIFEST)
            (run_dir / "back-implement-to-plan-1.md").write_text("packet", encoding="utf-8")
            findings = manifest_checks.check_backward_edge_counts(run_dir)
            self.assertEqual(
                [f for f in findings if f.severity == "error"], [],
                "Matching counts should produce no findings",
            )

    def test_mismatch_detected(self) -> None:
        """Manifest says 1, disk has 2 → mismatch finding."""
        with tempfile.TemporaryDirectory() as tmpdir:
            run_dir = _make_run_dir(tmpdir, self.MANIFEST)
            (run_dir / "back-implement-to-plan-1.md").write_text("p1", encoding="utf-8")
            (run_dir / "back-code-review-to-plan-1.md").write_text("p2", encoding="utf-8")
            findings = manifest_checks.check_backward_edge_counts(run_dir)
            errors = [f for f in findings if f.severity == "error"]
            self.assertTrue(
                any("mismatch" in f.message.lower() for f in errors),
                f"Should detect mismatch: {[f.message for f in errors]}",
            )

    def test_code_review_phase_parsed(self) -> None:
        """The 'Code Review' display name maps to 'code-review' phase id."""
        manifest = self.MANIFEST.replace(
            "### Phase 4: Code Review\n- Status: not-started\n- Backward edges received: 0",
            "### Phase 4: Code Review\n- Status: backward-edge-received\n- Backward edges received: 1",
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            run_dir = _make_run_dir(tmpdir, manifest)
            (run_dir / "back-implement-to-plan-1.md").write_text("p1", encoding="utf-8")
            (run_dir / "back-research-to-code-review-1.md").write_text("p2", encoding="utf-8")
            manifest_text = (run_dir / "00-run-manifest.md").read_text(encoding="utf-8")
            counts = manifest_checks._parse_backward_edge_counts_from_manifest(manifest_text)
            self.assertEqual(counts.get("code-review"), 1)
            # Directly assert the disk parser handles the hyphenated phase name
            # "code-review" (the key fix claimed by dw-003).
            disk_counts = manifest_checks._parse_backward_edge_counts_from_disk(run_dir)
            self.assertEqual(
                disk_counts.get("code-review"), 1,
                f"Disk parser must map back-*-to-code-review-N.md to 'code-review': {disk_counts}",
            )


class BackwardPacketFindingIdTests(unittest.TestCase):
    """dw-004: backward-packet finding-id validation reads Source artifact field."""

    def test_code_review_packet_bogus_id_caught(self) -> None:
        """A code-review packet referencing a bogus cr-999 is flagged."""
        with tempfile.TemporaryDirectory() as tmpdir:
            run_dir = _make_run_dir(tmpdir)
            (run_dir / "40-code-review.md").write_text(
                "# Code Review Report\n## Verdict\nneeds revision\n\ncr-001 real\n",
                encoding="utf-8",
            )
            packet = run_dir / "back-code-review-to-plan-1.md"
            packet.write_text(
                "# Backward Handoff Packet\n\n## Routing\n- From phase: code-review\n"
                "- To phase: plan\n- Backward edge count for target phase: 1 of 2\n\n"
                "## Source finding\n- Finding id: cr-999\n- Severity: major\n"
                "- Source artifact: 40-code-review.md\n",
                encoding="utf-8",
            )
            findings = handoff_checks.check_backward_packet_finding_exists(run_dir, packet)
            self.assertTrue(
                any("cr-999" in f.message for f in findings),
                f"Bogus cr-999 should be flagged: {[f.message for f in findings]}",
            )

    def test_research_packet_bogus_id_caught(self) -> None:
        """A research packet referencing a bogus rr-999 is flagged."""
        with tempfile.TemporaryDirectory() as tmpdir:
            run_dir = _make_run_dir(tmpdir)
            (run_dir / "11-research-review.md").write_text(
                "## Verdict\nneeds revision\n\nrr-001 real\n", encoding="utf-8",
            )
            packet = run_dir / "back-research-to-clarify-1.md"
            packet.write_text(
                "# Backward Handoff Packet\n\n## Routing\n- From phase: research\n"
                "- To phase: clarify\n- Backward edge count for target phase: 1 of 2\n\n"
                "## Source finding\n- Finding id: rr-999\n- Severity: major\n"
                "- Source artifact: 11-research-review.md\n",
                encoding="utf-8",
            )
            findings = handoff_checks.check_backward_packet_finding_exists(run_dir, packet)
            self.assertTrue(
                any("rr-999" in f.message for f in findings),
                f"Bogus rr-999 should be flagged: {[f.message for f in findings]}",
            )


class StagedModeAwarenessTests(unittest.TestCase):
    """dw-005: staged-mode awareness in loop_checks, handoff_checks, check_pre_phase."""

    STAGED_MANIFEST = "# Run Manifest\n\n## Run metadata\n- Run mode: staged\n"

    def test_staged_loop_checks_validate_stage_artifacts(self) -> None:
        """loop_checks validates stage-indexed checker/doer artifacts in staged mode."""
        with tempfile.TemporaryDirectory() as tmpdir:
            run_dir = _make_run_dir(tmpdir, self.STAGED_MANIFEST)
            (run_dir / "30-stage1-implementation-report.md").write_text(
                "# Implementation Report\n## Files changed\n- foo.py\n", encoding="utf-8",
            )
            (run_dir / "31-stage1-implementation-audit.md").write_text(
                "## Verdict\npass\n", encoding="utf-8",
            )
            # Verdict check should find and validate the stage-indexed audit.
            self.assertEqual(
                loop_checks.check_verdict_valid(run_dir, "implement"), [],
            )
            # Root-cause check should not error (no findings → no check needed).
            self.assertEqual(
                loop_checks.check_root_cause_phase_present(run_dir, "implement"), [],
            )

    def test_staged_loop_checks_read_stage_audit_content(self) -> None:
        """Negative control: an invalid verdict in the stage-indexed audit is flagged.

        Proves check_verdict_valid actually reads 31-stageN-implementation-audit.md;
        a regression to exact-filename resolution would return [] vacuously.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            run_dir = _make_run_dir(tmpdir, self.STAGED_MANIFEST)
            (run_dir / "31-stage1-implementation-audit.md").write_text(
                "## Verdict\nbogus verdict\n", encoding="utf-8",
            )
            findings = loop_checks.check_verdict_valid(run_dir, "implement")
            self.assertTrue(
                any("Invalid verdict" in f.message for f in findings),
                f"Invalid verdict in stage-indexed audit must be flagged: "
                f"{[f.message for f in findings]}",
            )

    def test_staged_loop_checks_require_root_cause_on_stage_findings(self) -> None:
        """Negative control: stage-audit findings without root-cause-phase are flagged.

        Proves check_root_cause_phase_present actually reads the stage-indexed
        audit; a regression to exact-filename resolution would return [] vacuously.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            run_dir = _make_run_dir(tmpdir, self.STAGED_MANIFEST)
            (run_dir / "31-stage1-implementation-audit.md").write_text(
                "## Verdict\nfail\n\nia-001: bug\n", encoding="utf-8",
            )
            findings = loop_checks.check_root_cause_phase_present(run_dir, "implement")
            self.assertTrue(
                any("root-cause-phase" in f.message for f in findings),
                f"Findings without root-cause-phase must be flagged: "
                f"{[f.message for f in findings]}",
            )

    def test_staged_handoff_checks_resolve_stage_report(self) -> None:
        """handoff_checks resolves stage-indexed implementation report in staged mode."""
        with tempfile.TemporaryDirectory() as tmpdir:
            run_dir = _make_run_dir(tmpdir, self.STAGED_MANIFEST)
            (run_dir / "30-stage1-implementation-report.md").write_text(
                "# Implementation Report\n## Files changed\n- foo.py\n", encoding="utf-8",
            )
            self.assertEqual(
                handoff_checks.check_impl_report_consumer_ready(run_dir), [],
            )

    def test_staged_handoff_checks_read_stage_report_content(self) -> None:
        """Negative control: a stage report missing '## Files changed' is flagged.

        Proves check_impl_report_consumer_ready actually reads
        30-stageN-implementation-report.md; a regression to exact-filename
        resolution would return [] vacuously.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            run_dir = _make_run_dir(tmpdir, self.STAGED_MANIFEST)
            (run_dir / "30-stage1-implementation-report.md").write_text(
                "# Implementation Report\n", encoding="utf-8",
            )
            findings = handoff_checks.check_impl_report_consumer_ready(run_dir)
            self.assertTrue(
                any("## Files changed" in f.message for f in findings),
                f"Stage report missing '## Files changed' must be flagged: "
                f"{[f.message for f in findings]}",
            )

    def test_staged_pre_flight_accepts_stage_impl_report(self) -> None:
        """check_pre_phase accepts stage-indexed impl report for code-review phase."""
        with tempfile.TemporaryDirectory() as tmpdir:
            run_dir = _make_run_dir(tmpdir, self.STAGED_MANIFEST)
            (run_dir / "30-stage1-implementation-report.md").write_text(
                "# Implementation Report\n", encoding="utf-8",
            )
            findings = check_pre_phase.run_pre_flight(run_dir, "code-review")
            self.assertEqual(
                [f for f in findings if f.severity == "error"], [],
                f"Staged pre-flight should accept stage-indexed impl report: "
                f"{[f.message for f in findings]}",
            )

    def test_staged_pre_flight_accepts_final_deep_review(self) -> None:
        """check_pre_phase accepts 40-final-deep-review.md for commit phase in staged mode."""
        with tempfile.TemporaryDirectory() as tmpdir:
            run_dir = _make_run_dir(tmpdir, self.STAGED_MANIFEST)
            (run_dir / "40-final-deep-review.md").write_text(
                "# Code Review Report\n", encoding="utf-8",
            )
            findings = check_pre_phase.run_pre_flight(run_dir, "commit")
            self.assertEqual(
                [f for f in findings if f.severity == "error"], [],
                f"Staged pre-flight should accept final deep review for commit: "
                f"{[f.message for f in findings]}",
            )


class StagedModeCommitPermissionTests(unittest.TestCase):
    """dw-006: staged-mode commit permission for implement/code-review phases."""

    def _make_git_repo(self, repo_root: Path) -> None:
        """Create a committed git repository for baseline/commit tests."""
        repo_root.mkdir(parents=True, exist_ok=True)
        for command in (
            ["git", "init", "-q"],
            ["git", "config", "user.email", "test@example.com"],
            ["git", "config", "user.name", "Test User"],
        ):
            subprocess.run(command, cwd=repo_root, check=True, capture_output=True)
        (repo_root / "src.py").write_text("value = 1\n", encoding="utf-8")
        subprocess.run(["git", "add", "src.py"], cwd=repo_root, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-qm", "initial"],
            cwd=repo_root, check=True, capture_output=True,
        )

    def _commit_a_change(self, repo_root: Path) -> None:
        """Make one additional commit in the repository."""
        (repo_root / "src.py").write_text("value = 2\n", encoding="utf-8")
        subprocess.run(["git", "add", "src.py"], cwd=repo_root, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-qm", "change"],
            cwd=repo_root, check=True, capture_output=True,
        )

    def test_linear_implement_blocks_commits(self) -> None:
        """In linear mode, an implement-phase commit produces an error finding."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir) / "repo"
            self._make_git_repo(repo_root)
            run_dir = repo_root / ".ai" / "workflow" / "run"
            run_dir.mkdir(parents=True, exist_ok=True)
            (run_dir / "00-run-manifest.md").write_text(
                "# Run Manifest\n\n## Run metadata\n- Run mode: linear\n", encoding="utf-8",
            )
            # Record the baseline at the current HEAD, then commit.
            baseline_head = subprocess.run(
                ["git", "rev-parse", "HEAD"], cwd=repo_root,
                check=True, capture_output=True, text=True,
            ).stdout.strip()
            (run_dir / "baseline.txt").write_text(baseline_head + "\n", encoding="utf-8")
            self._commit_a_change(repo_root)
            findings = mode_checks.check_no_commits_in_non_commit_phase(
                repo_root, "implement", run_dir,
            )
            self.assertTrue(
                any("made a commit" in f.message for f in findings),
                f"Linear implement-phase commit should be flagged: {[f.message for f in findings]}",
            )

    def test_staged_implement_allows_commits(self) -> None:
        """In staged mode, an implement-phase commit is permitted (no finding)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir) / "repo"
            self._make_git_repo(repo_root)
            run_dir = repo_root / ".ai" / "workflow" / "run"
            run_dir.mkdir(parents=True, exist_ok=True)
            (run_dir / "00-run-manifest.md").write_text(
                "# Run Manifest\n\n## Run metadata\n- Run mode: staged\n", encoding="utf-8",
            )
            baseline_head = subprocess.run(
                ["git", "rev-parse", "HEAD"], cwd=repo_root,
                check=True, capture_output=True, text=True,
            ).stdout.strip()
            (run_dir / "baseline.txt").write_text(baseline_head + "\n", encoding="utf-8")
            self._commit_a_change(repo_root)
            findings = mode_checks.check_no_commits_in_non_commit_phase(
                repo_root, "implement", run_dir,
            )
            self.assertEqual(
                findings, [],
                f"Staged implement-phase commit should be allowed: {[f.message for f in findings]}",
            )

    def test_staged_code_review_allows_commits(self) -> None:
        """In staged mode, a code-review-phase commit is permitted (no finding)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir) / "repo"
            self._make_git_repo(repo_root)
            run_dir = repo_root / ".ai" / "workflow" / "run"
            run_dir.mkdir(parents=True, exist_ok=True)
            (run_dir / "00-run-manifest.md").write_text(
                "# Run Manifest\n\n## Run metadata\n- Run mode: staged\n", encoding="utf-8",
            )
            baseline_head = subprocess.run(
                ["git", "rev-parse", "HEAD"], cwd=repo_root,
                check=True, capture_output=True, text=True,
            ).stdout.strip()
            (run_dir / "baseline.txt").write_text(baseline_head + "\n", encoding="utf-8")
            self._commit_a_change(repo_root)
            findings = mode_checks.check_no_commits_in_non_commit_phase(
                repo_root, "code-review", run_dir,
            )
            self.assertEqual(
                findings, [],
                f"Staged code-review-phase commit should be allowed: {[f.message for f in findings]}",
            )


class CodeReviewLoopOrderingTests(unittest.TestCase):
    """cr-001: code-review loop end-state mtime semantics.

    Validation runs on an accept verdict, and the accept verdict is written by
    the reviewer into 40-code-review.md — so at validation time the checker
    artifact must be the newest of the pair, in every phase including
    code-review. A completed loop ends with the reviewer consuming the fix
    report.
    """

    def test_converged_two_round_loop_passes(self) -> None:
        """Review → fix report → re-review (accept): 40 newest → no finding.

        This is the normal end state of every converging multi-round loop.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            run_dir = _make_run_dir(tmpdir)
            # Round 1 review (needs revision)
            (run_dir / "40-code-review.md").write_text(
                "# Code Review Report\n## Verdict\nneeds revision\n", encoding="utf-8",
            )
            _set_mtime(run_dir / "40-code-review.md")
            # Round 1 fixes
            (run_dir / "41-fix-report.md").write_text(
                "# Fix Report\n## Summary\nfixed cr-001\n", encoding="utf-8",
            )
            _set_mtime(run_dir / "41-fix-report.md")
            # Round 2 re-review (accept) — overwrites 40, newest write
            (run_dir / "40-code-review.md").write_text(
                "# Code Review Report\n## Verdict\nready to commit\n", encoding="utf-8",
            )
            _set_mtime(run_dir / "40-code-review.md")
            self.assertEqual(
                loop_checks.check_doer_precedes_checker(run_dir, "code-review"), [],
                "Converged loop (re-review newest) must pass validation",
            )

    def test_fix_report_newer_than_final_review_fails(self) -> None:
        """Fix report written after the final review with no re-review → finding.

        If 41 is newer than 40, the loop ended on the resolver without the
        reviewer consuming the fix report — an incomplete loop.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            run_dir = _make_run_dir(tmpdir)
            (run_dir / "40-code-review.md").write_text(
                "# Code Review Report\n## Verdict\nneeds revision\n", encoding="utf-8",
            )
            _set_mtime(run_dir / "40-code-review.md")
            (run_dir / "41-fix-report.md").write_text(
                "# Fix Report\n## Summary\nfixed\n", encoding="utf-8",
            )
            _set_mtime(run_dir / "41-fix-report.md")
            findings = loop_checks.check_doer_precedes_checker(run_dir, "code-review")
            self.assertTrue(
                len(findings) > 0,
                "Fix report newer than final review (no re-review) should be flagged",
            )

    def test_staged_same_stage_pair_compared(self) -> None:
        """Staged mode: same-stage review/fix-report pair is compared (cr-003)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            run_dir = _make_run_dir(tmpdir, "# Run Manifest\n\n## Run metadata\n- Run mode: staged\n")
            # Stage 1 converged loop: review → fix → re-review (newest)
            (run_dir / "40-stage1-code-review.md").write_text(
                "## Verdict\nneeds revision\n", encoding="utf-8",
            )
            _set_mtime(run_dir / "40-stage1-code-review.md")
            (run_dir / "41-stage1-fix-report.md").write_text(
                "# Fix Report\n## Summary\n", encoding="utf-8",
            )
            _set_mtime(run_dir / "41-stage1-fix-report.md")
            (run_dir / "40-stage1-code-review.md").write_text(
                "## Verdict\nready to commit\n", encoding="utf-8",
            )
            _set_mtime(run_dir / "40-stage1-code-review.md")
            self.assertEqual(
                loop_checks.check_doer_precedes_checker(run_dir, "code-review"), [],
                "Same-stage converged pair must pass",
            )

    def test_staged_cross_stage_pair_skipped(self) -> None:
        """Staged mode: cross-stage pairing is skipped, not flagged (cr-003)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            run_dir = _make_run_dir(tmpdir, "# Run Manifest\n\n## Run metadata\n- Run mode: staged\n")
            # Stage 1 review only (old), stage 2 fix report (new) — cross-stage.
            (run_dir / "40-stage1-code-review.md").write_text(
                "## Verdict\nneeds revision\n", encoding="utf-8",
            )
            _set_mtime(run_dir / "40-stage1-code-review.md")
            (run_dir / "41-stage2-fix-report.md").write_text(
                "# Fix Report\n## Summary\n", encoding="utf-8",
            )
            _set_mtime(run_dir / "41-stage2-fix-report.md")
            self.assertEqual(
                loop_checks.check_doer_precedes_checker(run_dir, "code-review"), [],
                "Cross-stage pairing must be skipped (ambiguous), not flagged",
            )


class ReadyWithNotesTests(unittest.TestCase):
    """cr-002: accepted reviews with minor findings need no fix report."""

    def test_ready_with_notes_and_minor_findings_passes(self) -> None:
        """`ready with notes` + minor cr-NNN findings → no fix-report error.

        `ready with notes` is an accept verdict: the loop exits forward, the
        resolver never runs, so no fix report exists.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            run_dir = _make_run_dir(tmpdir)
            (run_dir / "40-code-review.md").write_text(
                "# Code Review Report\n\n## Verdict\nready with notes\n\n"
                "#### cr-001: minor naming inconsistency\n#### cr-002: minor doc typo\n",
                encoding="utf-8",
            )
            findings = artifact_checks.run_all(run_dir, "code-review")
            errors = [f for f in findings if f.severity == "error"]
            self.assertEqual(
                errors, [],
                f"Accepted review with minor findings must not require a fix report: "
                f"{[f.message for f in errors]}",
            )

    def test_needs_revision_still_requires_fix_report(self) -> None:
        """`needs revision` verdict still requires the fix report (regression)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            run_dir = _make_run_dir(tmpdir)
            (run_dir / "40-code-review.md").write_text(
                "# Code Review Report\n\n## Verdict\nneeds revision\n\ncr-001: bug\n",
                encoding="utf-8",
            )
            findings = artifact_checks.run_all(run_dir, "code-review")
            errors = [f for f in findings if f.severity == "error"]
            self.assertTrue(
                any("41-fix-report.md" in f.message for f in errors),
                f"needs-revision verdict must still require the fix report: "
                f"{[f.message for f in errors]}",
            )


class StagedFinalArtifactTests(unittest.TestCase):
    """cr-007: staged-mode final deep review / final fix report recognized.

    Regression for the cr-001/cr-002 fix: in staged mode, the final deep
    review (40-final-deep-review.md) and final fix report
    (41-final-fix-report.md) must satisfy the canonical code-review artifact
    requirements, and the mtime check must compare the final pair.
    """

    STAGED_MANIFEST = "# Run Manifest\n\n## Run metadata\n- Run mode: staged\n"

    def test_final_deep_review_satisfies_code_review_artifact(self) -> None:
        """40-final-deep-review.md satisfies the 40-code-review.md requirement."""
        with tempfile.TemporaryDirectory() as tmpdir:
            run_dir = _make_run_dir(tmpdir, self.STAGED_MANIFEST)
            (run_dir / "40-final-deep-review.md").write_text(
                "# Code Review Report\n\n## Verdict\nready to commit\n",
                encoding="utf-8",
            )
            findings = artifact_checks.check_artifacts_exist(run_dir, "code-review")
            errors = [f for f in findings if f.severity == "error"]
            self.assertEqual(
                [f for f in errors if "40-code-review.md" in f.message], [],
                f"Final deep review must satisfy 40-code-review.md: {[f.message for f in errors]}",
            )

    def test_final_fix_report_satisfies_fix_report_artifact(self) -> None:
        """41-final-fix-report.md satisfies the 41-fix-report.md requirement."""
        with tempfile.TemporaryDirectory() as tmpdir:
            run_dir = _make_run_dir(tmpdir, self.STAGED_MANIFEST)
            (run_dir / "40-final-deep-review.md").write_text(
                "# Code Review Report\n\n## Verdict\nneeds revision\n\ncr-001: bug\n",
                encoding="utf-8",
            )
            (run_dir / "41-final-fix-report.md").write_text(
                "# Fix Report\n## Summary\nfixed cr-001\n", encoding="utf-8",
            )
            findings = artifact_checks.check_artifacts_exist(run_dir, "code-review")
            errors = [f for f in findings if f.severity == "error"]
            self.assertEqual(
                [f for f in errors if "41-fix-report.md" in f.message], [],
                f"Final fix report must satisfy 41-fix-report.md: {[f.message for f in errors]}",
            )

    def test_final_pair_mtime_checked(self) -> None:
        """Final fix report newer than final deep review (no re-review) → flagged."""
        with tempfile.TemporaryDirectory() as tmpdir:
            run_dir = _make_run_dir(tmpdir, self.STAGED_MANIFEST)
            (run_dir / "40-final-deep-review.md").write_text(
                "# Code Review Report\n\n## Verdict\nneeds revision\n", encoding="utf-8",
            )
            _set_mtime(run_dir / "40-final-deep-review.md")
            (run_dir / "41-final-fix-report.md").write_text(
                "# Fix Report\n## Summary\nfixed\n", encoding="utf-8",
            )
            _set_mtime(run_dir / "41-final-fix-report.md")
            findings = loop_checks.check_doer_precedes_checker(run_dir, "code-review")
            self.assertTrue(
                len(findings) > 0,
                "Final fix report newer than final deep review must be flagged",
            )

    def test_final_pair_converged_passes(self) -> None:
        """Final deep review (accept) newer than final fix report → no finding."""
        with tempfile.TemporaryDirectory() as tmpdir:
            run_dir = _make_run_dir(tmpdir, self.STAGED_MANIFEST)
            (run_dir / "40-final-deep-review.md").write_text(
                "# Code Review Report\n\n## Verdict\nneeds revision\n", encoding="utf-8",
            )
            _set_mtime(run_dir / "40-final-deep-review.md")
            (run_dir / "41-final-fix-report.md").write_text(
                "# Fix Report\n## Summary\nfixed\n", encoding="utf-8",
            )
            _set_mtime(run_dir / "41-final-fix-report.md")
            (run_dir / "40-final-deep-review.md").write_text(
                "# Code Review Report\n\n## Verdict\nready to commit\n", encoding="utf-8",
            )
            _set_mtime(run_dir / "40-final-deep-review.md")
            self.assertEqual(
                loop_checks.check_doer_precedes_checker(run_dir, "code-review"), [],
                "Converged final pair (re-review newest) must pass",
            )


class PerStageReviewFindingsTests(unittest.TestCase):
    """cr-008: per-stage reviews explicitly inspected for findings (cr-003 fix).

    A per-stage review (40-stageN-code-review.md) with a `needs revision`
    verdict must require a fix report, even when no 40-code-review.md or
    40-final-deep-review.md exists.
    """

    def test_per_stage_needs_revision_requires_fix_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            run_dir = _make_run_dir(tmpdir, "# Run Manifest\n\n## Run metadata\n- Run mode: staged\n")
            (run_dir / "40-stage1-code-review.md").write_text(
                "# Code Review Report\n\n## Verdict\nneeds revision\n\ncr-001: bug\n",
                encoding="utf-8",
            )
            self.assertTrue(
                artifact_checks._code_review_has_findings(run_dir, staged_mode=True),
                "Per-stage needs-revision review must require a fix report",
            )

    def test_per_stage_accept_no_fix_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            run_dir = _make_run_dir(tmpdir, "# Run Manifest\n\n## Run metadata\n- Run mode: staged\n")
            (run_dir / "40-stage1-code-review.md").write_text(
                "# Code Review Report\n\n## Verdict\nready to commit\n", encoding="utf-8",
            )
            self.assertFalse(
                artifact_checks._code_review_has_findings(run_dir, staged_mode=True),
                "Per-stage accept verdict must not require a fix report",
            )


class OverallVerdictListItemTests(unittest.TestCase):
    """cr-009: ``- Overall verdict:`` list-item form matched (cr-004 fix)."""

    def test_overall_verdict_list_item(self) -> None:
        """``- Overall verdict: <value>`` after ``## Overall verdict`` heading."""
        text = "## Overall verdict\n- Overall verdict: ready to commit\n"
        self.assertEqual(verdicts.extract_verdict(text), "ready to commit")

    def test_overall_verdict_numbered_heading_with_list_item(self) -> None:
        """``## 8. Overall verdict`` + ``- Overall verdict: <value>``."""
        text = "## 8. Overall verdict\n- Overall verdict: needs revision\n"
        self.assertEqual(verdicts.extract_verdict(text), "needs revision")


class VerdictSubstringMatchingTests(unittest.TestCase):
    """cr-010: verdict matching uses match_verdict, not substring (cr-005 fix).

    An accept verdict whose context text contains the phrase "needs revision"
    must NOT trigger a fix-report requirement.
    """

    def test_accept_verdict_with_needs_revision_phrase_no_fix_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            run_dir = _make_run_dir(tmpdir)
            (run_dir / "40-code-review.md").write_text(
                "# Code Review Report\n\n## Verdict\n"
                "ready with notes — minor needs revision in docs noted\n",
                encoding="utf-8",
            )
            self.assertFalse(
                artifact_checks._code_review_has_findings(run_dir, staged_mode=False),
                "Accept verdict containing 'needs revision' phrase must not require a fix report",
            )


class OrphanDiskPacketTests(unittest.TestCase):
    """cr-011: orphan disk packets for un-manifested phases flagged (cr-008 fix)."""

    MANIFEST_NO_BACKWARD_LINES = """# Run Manifest

## Run metadata
- Current phase: plan
- Run status: in-progress

## Phase status

### Phase 0: Clarify
- Status: accepted

### Phase 1: Research
- Status: accepted

### Phase 2: Plan
- Status: not-started

### Phase 3: Implement
- Status: not-started

### Phase 4: Code Review
- Status: not-started
"""

    def test_orphan_packets_for_unmanifested_phase_flagged(self) -> None:
        """Disk packets for a phase with no manifest 'Backward edges received' line → finding."""
        with tempfile.TemporaryDirectory() as tmpdir:
            run_dir = _make_run_dir(tmpdir, self.MANIFEST_NO_BACKWARD_LINES)
            for i in range(1, 4):
                (run_dir / f"back-implement-to-plan-{i}.md").write_text("p", encoding="utf-8")
            findings = manifest_checks.check_backward_edge_counts(run_dir)
            self.assertTrue(
                any("no 'Backward edges received' entry" in f.message for f in findings),
                f"Orphan packets for un-manifested phase must be flagged: {[f.message for f in findings]}",
            )


class BackwardPacketStageIndexedSourceTests(unittest.TestCase):
    """cr-012: backward packet resolves stage-indexed source artifact (cr-009 fix).

    A packet declaring ``Source artifact: 40-code-review.md`` must still find
    a bogus finding id when only ``40-stage1-code-review.md`` exists on disk.
    """

    def test_stage_indexed_source_resolved(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            run_dir = _make_run_dir(tmpdir, "# Run Manifest\n\n## Run metadata\n- Run mode: staged\n")
            (run_dir / "40-stage1-code-review.md").write_text(
                "# Code Review Report\n\n## Verdict\nneeds revision\n\ncr-001 real\n",
                encoding="utf-8",
            )
            packet = run_dir / "back-code-review-to-plan-1.md"
            packet.write_text(
                "# Backward Handoff Packet\n\n## Routing\n- From phase: code-review\n"
                "- To phase: plan\n- Backward edge count for target phase: 1 of 2\n\n"
                "## Source finding\n- Finding id: cr-999\n- Severity: major\n"
                "- Source artifact: 40-code-review.md\n",
                encoding="utf-8",
            )
            findings = handoff_checks.check_backward_packet_finding_exists(run_dir, packet)
            self.assertTrue(
                any("cr-999" in f.message for f in findings),
                f"Bogus cr-999 against stage-indexed source must be flagged: {[f.message for f in findings]}",
            )


if __name__ == "__main__":
    unittest.main()
