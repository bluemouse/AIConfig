#!/usr/bin/env python3
"""Dry-run test for the dev-workflow validation scripts.

Creates temporary run directories with various artifact configurations and
verifies that the validation scripts produce the expected results.

Usage:
    python tools/dev-workflow/test_dry_run.py

Exit codes:
    0 — all tests passed
    1 — one or more tests failed
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def write_file(path: Path, content: str) -> None:
    """Write content to a file, creating parent directories."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def run_validator(script: str, args: list[str]) -> tuple[int, str]:
    """Run a validation script and return (exit_code, stdout)."""
    result = subprocess.run(
        [sys.executable, f"tools/dev-workflow/{script}", *args],
        capture_output=True,
        text=True,
        timeout=30,
    )
    return result.returncode, result.stdout + result.stderr


class DryRunTest:
    """Test runner for dev-workflow validation scripts."""

    def __init__(self) -> None:
        self.passed = 0
        self.failed = 0
        self.temp_dir = Path(tempfile.mkdtemp(prefix="dev-workflow-test-"))

    def cleanup(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def assert_contains(self, output: str, expected: str, test_name: str) -> bool:
        if expected in output:
            self.passed += 1
            print(f"  PASS: {test_name}")
            return True
        self.failed += 1
        print(f"  FAIL: {test_name}")
        print(f"    Expected output to contain: {expected!r}")
        print(f"    Got: {output!r}")
        return False

    def assert_exit_code(self, code: int, expected: int, test_name: str) -> bool:
        if code == expected:
            self.passed += 1
            print(f"  PASS: {test_name}")
            return True
        self.failed += 1
        print(f"  FAIL: {test_name}")
        print(f"    Expected exit code {expected}, got {code}")
        return False

    def make_manifest(self, run_dir: Path, phase: str = "research",
                      status: str = "in-progress", backward_edges: dict[str, int] | None = None) -> None:
        """Write a valid manifest."""
        backward_edges = backward_edges or {}
        be_clarify = backward_edges.get("clarify", 0)
        be_research = backward_edges.get("research", 0)
        be_plan = backward_edges.get("plan", 0)
        be_implement = backward_edges.get("implement", 0)
        be_review = backward_edges.get("code-review", 0)

        write_file(run_dir / "00-run-manifest.md", f"""# Run Manifest

## Run metadata
- Feature slug: test-feature
- Created: 2026-08-22T10:00:00Z
- Last updated: 2026-08-22T10:00:00Z
- Current phase: {phase}
- Run status: {status}

## Input
- Requirement: Test feature for dry-run
- Feature brief: 01-feature-brief.md

## Phase status

### Phase 0: Clarify
- Status: not-started
- Terminal artifact: 02-requirement-ledger.md
- Backward edges received: {be_clarify}

### Phase 1: Research
- Status: in-progress
- Current round: 1
- Terminal artifact: 10-research-report.md
- Backward edges received: {be_research}

### Phase 2: Plan
- Status: not-started
- Current round: 1
- Terminal artifact: 20-implementation-plan.md
- Backward edges received: {be_plan}

### Phase 3: Implement
- Status: not-started
- Current round: 1
- Terminal artifact: 30-implementation-report.md
- Backward edges received: {be_implement}

### Phase 4: Code Review
- Status: not-started
- Current round: 1
- Backward edges received: {be_review}

### Phase 5: Commit
- Status: not-started
- Terminal artifact: 50-commit.md

## Artifact registry
| Artifact | Path | Phase | Status |
|----------|------|-------|--------|
| Manifest | 00-run-manifest.md | 0 | final |

## Backward edge log
| # | From | To | Finding id | Packet path | Resolved |
|---|------|----|-----------|-------------|----------|

## Validation log
| Phase | Check | Severity | Finding | Orchestrator decision | Justification |
|-------|-------|----------|---------|----------------------|---------------|
""")

    def make_feature_brief(self, run_dir: Path) -> None:
        write_file(run_dir / "01-feature-brief.md", "# Feature Brief\n\nTest feature for dry-run.\n")

    def make_requirement_ledger(self, run_dir: Path) -> None:
        write_file(run_dir / "02-requirement-ledger.md", """# Requirement Ledger

## Outcome
Test outcome.

## Scope
- In scope: test scope
- Out of scope: nothing

## Acceptance criteria
Test passes.

## Assumptions
None.
""")

    def make_research_artifacts(self, run_dir: Path, verdict: str = "ready",
                                  include_root_cause: bool = False) -> None:
        rc_field = ""
        if include_root_cause:
            rc_field = "\n- root-cause-phase: local"
        write_file(run_dir / "10-research-report.md", """# Research Report

## Problem statement
Test problem.

## Goals
Test goals.

## Requirements
Test requirements.
""")
        write_file(run_dir / "11-research-review.md", f"""# Research Review Report

## Verdict

{verdict} — research is complete.

## Findings

### rr-001: Test finding
- Severity: minor
- Location: section 2{rc_field}
- Issue: minor gap
- Required fix: add detail
""")

    def make_plan_artifacts(self, run_dir: Path, verdict: str = "validated",
                             include_root_cause: bool = False) -> None:
        rc_field = ""
        if include_root_cause:
            rc_field = "\n- root-cause-phase: local"
        write_file(run_dir / "20-implementation-plan.md", """# Implementation Plan

## Planning status
Status: ready for review

## Task breakdown
1. Task one
""")
        write_file(run_dir / "21-plan-review.md", f"""# Plan Review Report

## Verdict

{verdict} — plan is ready.

## Findings

### pr-001: Test finding
- Severity: minor
- Location: task 1{rc_field}
- Issue: minor gap
- Required fix: add detail
""")

    def make_backward_packet(self, run_dir: Path, filename: str,
                               from_phase: str = "plan", to_phase: str = "research",
                               count: int = 1, finding_id: str = "pr-001") -> None:
        write_file(run_dir / filename, f"""# Backward Handoff Packet

## Routing
- From phase: {from_phase}
- To phase: {to_phase}
- Backward edge count for target phase: {count} of 2
- Created: 2026-08-22T11:00:00Z

## Source finding
- Finding id: {finding_id}
- Severity: major
- Source artifact: 21-plan-review.md

## Root cause classification
- Classification: upstream
- Why this is not a local defect: the research report lacks detail
- Why the target phase is the root: research is the first phase

## What the target phase must resolve
- Issue: missing detail
- Why it matters: plan cannot be validated without it
- Required fix: add detail to the research report
- Evidence: 10-research-report.md

## Context from the source phase
- What was attempted: tried to plan without detail
- Why local fix is insufficient: detail must come from research
- Artifacts to review: 21-plan-review.md
""")

    def make_git_repo(self, name: str) -> Path:
        """Create a committed repository for baseline and commit-mode tests."""
        repo_root = self.temp_dir / name
        repo_root.mkdir(parents=True, exist_ok=True)
        for command in (
            ["git", "init", "-q"],
            ["git", "config", "user.email", "test@example.com"],
            ["git", "config", "user.name", "Test User"],
        ):
            subprocess.run(command, cwd=repo_root, check=True, capture_output=True)
        write_file(repo_root / "src.py", "value = 1\n")
        subprocess.run(["git", "add", "src.py"], cwd=repo_root, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-qm", "initial"],
            cwd=repo_root,
            check=True,
            capture_output=True,
        )
        return repo_root

    def record_phase_baseline(self, run_dir: Path, repo_root: Path, phase: str) -> None:
        """Record a phase baseline and assert that setup completed."""
        code, output = run_validator(
            "record_baseline.py",
            ["--phase", phase, "--run-dir", str(run_dir), "--repo-root", str(repo_root)],
        )
        self.assert_exit_code(code, 0, "baseline recorded")
        self.assert_contains(output, "BASELINE RECORDED", "baseline output")

    # --- Tests ---

    def test_pre_flight_clarify_pass(self) -> None:
        """Pre-flight should pass for clarify phase when feature brief exists."""
        print("\n[Test] Pre-flight pass (clarify phase)")
        run_dir = self.temp_dir / "pre_flight_clarify"
        self.make_manifest(run_dir, phase="clarify")
        self.make_feature_brief(run_dir)
        code, output = run_validator("check_pre_phase.py", ["--phase", "clarify", "--run-dir", str(run_dir)])
        self.assert_exit_code(code, 0, "exit code 0")
        self.assert_contains(output, "PASSED", "output contains PASSED")

    def test_pre_flight_pass(self) -> None:
        """Pre-flight should pass when manifest and feature brief exist."""
        print("\n[Test] Pre-flight pass (research phase)")
        run_dir = self.temp_dir / "pre_flight_pass"
        self.make_manifest(run_dir)
        self.make_feature_brief(run_dir)
        self.make_requirement_ledger(run_dir)
        code, output = run_validator("check_pre_phase.py", ["--phase", "research", "--run-dir", str(run_dir)])
        self.assert_exit_code(code, 0, "exit code 0")
        self.assert_contains(output, "PASSED", "output contains PASSED")

    def test_pre_flight_fail_missing_input(self) -> None:
        """Pre-flight should fail when expected input artifact is missing."""
        print("\n[Test] Pre-flight fail (missing input artifact)")
        run_dir = self.temp_dir / "pre_flight_fail"
        self.make_manifest(run_dir)
        # Don't write requirement ledger (research's input)
        code, output = run_validator("check_pre_phase.py", ["--phase", "research", "--run-dir", str(run_dir)])
        self.assert_exit_code(code, 1, "exit code 1")
        self.assert_contains(output, "FAILED", "output contains FAILED")
        self.assert_contains(output, "02-requirement-ledger.md", "output mentions missing file")

    def test_validate_phase_clarify_pass(self) -> None:
        """Validate clarify phase should pass with a valid requirement ledger."""
        print("\n[Test] Validate phase (clarify) pass")
        run_dir = self.temp_dir / "validate_clarify_pass"
        self.make_manifest(run_dir, phase="clarify")
        self.make_feature_brief(run_dir)
        self.make_requirement_ledger(run_dir)
        code, output = run_validator("validate_phase.py", ["--phase", "clarify", "--run-dir", str(run_dir)])
        self.assert_exit_code(code, 0, "exit code 0")
        self.assert_contains(output, "PASSED", "output contains PASSED")

    def test_validate_phase_clarify_missing(self) -> None:
        """Validate clarify phase should fail when requirement ledger is missing."""
        print("\n[Test] Validate phase (clarify) fail — missing ledger")
        run_dir = self.temp_dir / "validate_clarify_missing"
        self.make_manifest(run_dir, phase="clarify")
        self.make_feature_brief(run_dir)
        code, output = run_validator("validate_phase.py", ["--phase", "clarify", "--run-dir", str(run_dir)])
        self.assert_exit_code(code, 1, "exit code 1")
        self.assert_contains(output, "FAILED", "output contains FAILED")
        self.assert_contains(output, "02-requirement-ledger.md", "output mentions missing ledger")

    def test_validate_phase_research_pass(self) -> None:
        """Validate research phase should pass with valid artifacts."""
        print("\n[Test] Validate phase (research) pass")
        run_dir = self.temp_dir / "validate_research_pass"
        self.make_manifest(run_dir)
        self.make_feature_brief(run_dir)
        self.make_research_artifacts(run_dir, verdict="ready", include_root_cause=True)
        code, output = run_validator("validate_phase.py", ["--phase", "research", "--run-dir", str(run_dir)])
        self.assert_exit_code(code, 0, "exit code 0")
        self.assert_contains(output, "PASSED", "output contains PASSED")

    def test_validate_phase_research_missing_artifacts(self) -> None:
        """Validate research phase should fail when artifacts are missing."""
        print("\n[Test] Validate phase (research) fail — missing artifacts")
        run_dir = self.temp_dir / "validate_research_missing"
        self.make_manifest(run_dir)
        self.make_feature_brief(run_dir)
        # Don't write research artifacts
        code, output = run_validator("validate_phase.py", ["--phase", "research", "--run-dir", str(run_dir)])
        self.assert_exit_code(code, 1, "exit code 1")
        self.assert_contains(output, "FAILED", "output contains FAILED")
        self.assert_contains(output, "10-research-report.md", "output mentions missing report")

    def test_validate_phase_invalid_verdict(self) -> None:
        """Validate should fail when verdict is not in the allowed set."""
        print("\n[Test] Validate phase (research) fail — invalid verdict")
        run_dir = self.temp_dir / "validate_invalid_verdict"
        self.make_manifest(run_dir)
        self.make_feature_brief(run_dir)
        self.make_research_artifacts(run_dir, verdict="good to go", include_root_cause=True)
        code, output = run_validator("validate_phase.py", ["--phase", "research", "--run-dir", str(run_dir)])
        self.assert_exit_code(code, 1, "exit code 1")
        self.assert_contains(output, "Invalid verdict", "output mentions invalid verdict")

    def test_validate_phase_missing_root_cause(self) -> None:
        """Validate should fail when root-cause-phase is missing from findings."""
        print("\n[Test] Validate phase (research) fail — missing root-cause-phase")
        run_dir = self.temp_dir / "validate_missing_rc"
        self.make_manifest(run_dir)
        self.make_feature_brief(run_dir)
        self.make_research_artifacts(run_dir, verdict="needs revision", include_root_cause=False)
        code, output = run_validator("validate_phase.py", ["--phase", "research", "--run-dir", str(run_dir)])
        self.assert_exit_code(code, 1, "exit code 1")
        self.assert_contains(output, "root-cause-phase", "output mentions root-cause-phase")

    def test_validate_backward_edge_pass(self) -> None:
        """Backward edge validation should pass with a valid packet."""
        print("\n[Test] Validate backward edge pass")
        run_dir = self.temp_dir / "backward_pass"
        self.make_manifest(run_dir)
        self.make_plan_artifacts(run_dir, verdict="needs revision", include_root_cause=True)
        self.make_backward_packet(run_dir, "back-plan-to-research-1.md",
                                  from_phase="plan", to_phase="research", finding_id="pr-001")
        code, output = run_validator("validate_backward_edge.py",
                                      ["--packet", str(run_dir / "back-plan-to-research-1.md"),
                                       "--run-dir", str(run_dir)])
        self.assert_exit_code(code, 0, "exit code 0")
        self.assert_contains(output, "PASSED", "output contains PASSED")

    def test_validate_backward_edge_target_later(self) -> None:
        """Backward edge validation should fail when target is a later phase."""
        print("\n[Test] Validate backward edge fail — target is later phase")
        run_dir = self.temp_dir / "backward_later"
        self.make_manifest(run_dir)
        self.make_research_artifacts(run_dir, include_root_cause=True)
        # Packet from research to plan (forward, not backward)
        self.make_backward_packet(run_dir, "back-research-to-plan-1.md",
                                  from_phase="research", to_phase="plan", finding_id="rr-001")
        code, output = run_validator("validate_backward_edge.py",
                                      ["--packet", str(run_dir / "back-research-to-plan-1.md"),
                                       "--run-dir", str(run_dir)])
        self.assert_exit_code(code, 1, "exit code 1")
        self.assert_contains(output, "later or same phase", "output mentions later phase")

    def test_validate_backward_edge_missing_fields(self) -> None:
        """Backward edge validation should fail when required fields are missing."""
        print("\n[Test] Validate backward edge fail — missing fields")
        run_dir = self.temp_dir / "backward_missing"
        self.make_manifest(run_dir)
        write_file(run_dir / "back-plan-to-research-1.md", """# Backward Handoff Packet

## Routing
- From phase: plan
- To phase: research
""")
        code, output = run_validator("validate_backward_edge.py",
                                      ["--packet", str(run_dir / "back-plan-to-research-1.md"),
                                       "--run-dir", str(run_dir)])
        self.assert_exit_code(code, 1, "exit code 1")
        self.assert_contains(output, "missing field", "output mentions missing field")

    def test_validate_backward_edge_cap_exceeded(self) -> None:
        """Backward edge validation should fail when cap is exceeded."""
        print("\n[Test] Validate backward edge fail — cap exceeded")
        run_dir = self.temp_dir / "backward_cap"
        self.make_manifest(run_dir, backward_edges={"research": 3})
        self.make_plan_artifacts(run_dir, include_root_cause=True)
        self.make_backward_packet(run_dir, "back-plan-to-research-3.md",
                                  from_phase="plan", to_phase="research", count=3, finding_id="pr-001")
        code, output = run_validator("validate_backward_edge.py",
                                      ["--packet", str(run_dir / "back-plan-to-research-3.md"),
                                       "--run-dir", str(run_dir)])
        self.assert_exit_code(code, 1, "exit code 1")
        self.assert_contains(output, "cap exceeded", "output mentions cap exceeded")

    def test_post_flight_pass(self) -> None:
        """Post-flight should pass when only allowed artifacts are written."""
        print("\n[Test] Post-flight pass (research phase)")
        run_dir = self.temp_dir / "post_flight_pass"
        self.make_manifest(run_dir)
        self.make_feature_brief(run_dir)
        self.make_research_artifacts(run_dir, include_root_cause=True)
        code, output = run_validator("check_post_phase.py", ["--phase", "research", "--run-dir", str(run_dir)])
        self.assert_exit_code(code, 0, "exit code 0")
        self.assert_contains(output, "PASSED", "output contains PASSED")

    def test_post_flight_wrong_artifact(self) -> None:
        """Post-flight should fail when a phase writes outside its allowed set."""
        print("\n[Test] Post-flight fail — wrong artifact prefix")
        run_dir = self.temp_dir / "post_flight_wrong"
        self.make_manifest(run_dir)
        self.make_feature_brief(run_dir)
        self.make_research_artifacts(run_dir, include_root_cause=True)
        # Write a plan artifact in research phase (should not be allowed)
        write_file(run_dir / "20-implementation-plan.md", "# Plan\n\nShould not be here.\n")
        code, output = run_validator("check_post_phase.py", ["--phase", "research", "--run-dir", str(run_dir)])
        self.assert_exit_code(code, 1, "exit code 1")
        self.assert_contains(output, "FAILED", "output contains FAILED")
        self.assert_contains(output, "outside its allowed set", "output mentions outside allowed set")

    def test_post_flight_dirty_source_mutation(self) -> None:
        """Post-flight must flag a read-only edit to an already-dirty source file."""
        print("\n[Test] Post-flight fail — changed dirty source")
        repo_root = self.make_git_repo("dirty_source")
        run_dir = repo_root / ".ai" / "workflow" / "run"
        self.make_manifest(run_dir)
        self.make_feature_brief(run_dir)
        write_file(repo_root / "src.py", "value = 2\n")
        self.record_phase_baseline(run_dir, repo_root, "research")
        write_file(repo_root / "src.py", "value = 3\n")
        code, output = run_validator(
            "check_post_phase.py",
            ["--phase", "research", "--run-dir", str(run_dir), "--repo-root", str(repo_root)],
        )
        self.assert_exit_code(code, 1, "exit code 1")
        self.assert_contains(output, "src.py", "output mentions changed source")

    def test_non_git_snapshot_preserves_existing_artifacts(self) -> None:
        """A no-Git baseline must hash existing workflow artifacts consistently."""
        print("\n[Test] Post-flight pass — no-Git snapshot")
        run_dir = self.temp_dir / "non_git_snapshot"
        self.make_manifest(run_dir)
        self.make_feature_brief(run_dir)
        code, output = run_validator(
            "record_baseline.py", ["--phase", "research", "--run-dir", str(run_dir)]
        )
        self.assert_exit_code(code, 0, "exit code 0")
        self.assert_contains(output, "not a git repository", "output mentions no-Git mode")
        self.make_research_artifacts(run_dir, include_root_cause=True)
        code, output = run_validator(
            "check_post_phase.py", ["--phase", "research", "--run-dir", str(run_dir)]
        )
        self.assert_exit_code(code, 0, "exit code 0")
        self.assert_contains(output, "PASSED", "output contains PASSED")

    def test_post_flight_existing_foreign_artifact_mutation(self) -> None:
        """Post-flight must flag changes to another phase's existing artifact."""
        print("\n[Test] Post-flight fail — changed existing foreign artifact")
        repo_root = self.make_git_repo("foreign_artifact")
        run_dir = repo_root / ".ai" / "workflow" / "run"
        self.make_manifest(run_dir)
        self.make_feature_brief(run_dir)
        self.make_plan_artifacts(run_dir, include_root_cause=True)
        self.record_phase_baseline(run_dir, repo_root, "research")
        write_file(run_dir / "20-implementation-plan.md", "# Implementation Plan\n\nChanged.\n")
        code, output = run_validator(
            "check_post_phase.py",
            ["--phase", "research", "--run-dir", str(run_dir), "--repo-root", str(repo_root)],
        )
        self.assert_exit_code(code, 1, "exit code 1")
        self.assert_contains(output, "20-implementation-plan.md", "output mentions foreign artifact")

    def test_post_flight_existing_foreign_artifact_deletion(self) -> None:
        """Post-flight must flag deletion of another phase's existing artifact."""
        print("\n[Test] Post-flight fail — deleted existing foreign artifact")
        repo_root = self.make_git_repo("deleted_foreign_artifact")
        run_dir = repo_root / ".ai" / "workflow" / "run"
        self.make_manifest(run_dir)
        self.make_feature_brief(run_dir)
        self.make_plan_artifacts(run_dir, include_root_cause=True)
        self.record_phase_baseline(run_dir, repo_root, "research")
        (run_dir / "20-implementation-plan.md").unlink()
        code, output = run_validator(
            "check_post_phase.py",
            ["--phase", "research", "--run-dir", str(run_dir), "--repo-root", str(repo_root)],
        )
        self.assert_exit_code(code, 1, "exit code 1")
        self.assert_contains(output, "deleted artifact", "output mentions deletion")

    def test_post_flight_manifest_mutation(self) -> None:
        """Post-flight must flag phase edits to the orchestrator-owned manifest."""
        print("\n[Test] Post-flight fail — manifest mutation")
        repo_root = self.make_git_repo("manifest_mutation")
        run_dir = repo_root / ".ai" / "workflow" / "run"
        self.make_manifest(run_dir)
        self.make_feature_brief(run_dir)
        self.record_phase_baseline(run_dir, repo_root, "research")
        write_file(run_dir / "00-run-manifest.md", "# Run Manifest\n\nTampered.\n")
        code, output = run_validator(
            "check_post_phase.py",
            ["--phase", "research", "--run-dir", str(run_dir), "--repo-root", str(repo_root)],
        )
        self.assert_exit_code(code, 1, "exit code 1")
        self.assert_contains(output, "orchestrator-owned", "output mentions manifest ownership")

    def test_commit_record_must_match_new_head(self) -> None:
        """Commit phase must reject a record pointing to an old unchanged HEAD."""
        print("\n[Test] Post-flight fail — unchanged commit HEAD")
        repo_root = self.make_git_repo("commit_record")
        run_dir = repo_root / ".ai" / "workflow" / "run"
        self.make_manifest(run_dir, phase="commit")
        self.make_feature_brief(run_dir)
        initial_head = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=repo_root, check=True,
            capture_output=True, text=True,
        ).stdout.strip()
        self.record_phase_baseline(run_dir, repo_root, "commit")
        write_file(run_dir / "50-commit.md", f"# Commit Record\n\nCommit hash: {initial_head}\n")
        code, output = run_validator(
            "check_post_phase.py",
            ["--phase", "commit", "--run-dir", str(run_dir), "--repo-root", str(repo_root)],
        )
        self.assert_exit_code(code, 1, "exit code 1")
        self.assert_contains(output, "did not advance HEAD", "output mentions unchanged HEAD")

    def test_loop_cap_uses_revision_suffixes(self) -> None:
        """Validation must reject revision artifacts whose suffix exceeds the cap."""
        print("\n[Test] Validate phase fail — revision suffix exceeds cap")
        run_dir = self.temp_dir / "loop_cap_suffix"
        self.make_manifest(run_dir)
        self.make_feature_brief(run_dir)
        self.make_research_artifacts(run_dir, include_root_cause=True)
        write_file(run_dir / "12-research-report-r6.md", "# Research Report\n")
        code, output = run_validator("validate_phase.py", ["--phase", "research", "--run-dir", str(run_dir)])
        self.assert_exit_code(code, 1, "exit code 1")
        self.assert_contains(output, "Loop cap exceeded", "output mentions loop cap")

    def test_loop_cap_ignores_other_phase_revisions(self) -> None:
        """A later phase's revision count must not invalidate Research."""
        print("\n[Test] Validate phase pass — ignore other phase revision suffix")
        run_dir = self.temp_dir / "loop_cap_other_phase"
        self.make_manifest(run_dir)
        self.make_feature_brief(run_dir)
        self.make_research_artifacts(run_dir, include_root_cause=True)
        write_file(run_dir / "22-implementation-plan-r99.md", "# Implementation Plan\n")
        code, output = run_validator("record_baseline.py", ["--phase", "research", "--run-dir", str(run_dir)])
        self.assert_exit_code(code, 0, "exit code 0")
        code, output = run_validator("validate_phase.py", ["--phase", "research", "--run-dir", str(run_dir)])
        self.assert_exit_code(code, 0, "exit code 0")
        self.assert_contains(output, "PASSED", "output contains PASSED")

    def test_checker_must_follow_doer(self) -> None:
        """Validation must reject a checker artifact older than its doer input."""
        print("\n[Test] Validate phase fail — checker precedes doer")
        run_dir = self.temp_dir / "checker_order"
        self.make_manifest(run_dir)
        self.make_feature_brief(run_dir)
        self.make_research_artifacts(run_dir, include_root_cause=True)
        checker = run_dir / "11-research-review.md"
        doer = run_dir / "10-research-report.md"
        timestamp = checker.stat().st_mtime_ns
        os.utime(doer, ns=(timestamp + 1, timestamp + 1))
        code, output = run_validator("validate_phase.py", ["--phase", "research", "--run-dir", str(run_dir)])
        self.assert_exit_code(code, 1, "exit code 1")
        self.assert_contains(output, "predates its doer", "output mentions artifact ordering")

    def run_all(self) -> int:
        """Run all dry-run tests."""
        print("=" * 60)
        print("Dev Workflow Dry-Run Test Suite")
        print("=" * 60)

        tests = [
            self.test_pre_flight_clarify_pass,
            self.test_pre_flight_pass,
            self.test_pre_flight_fail_missing_input,
            self.test_validate_phase_clarify_pass,
            self.test_validate_phase_clarify_missing,
            self.test_validate_phase_research_pass,
            self.test_validate_phase_research_missing_artifacts,
            self.test_validate_phase_invalid_verdict,
            self.test_validate_phase_missing_root_cause,
            self.test_validate_backward_edge_pass,
            self.test_validate_backward_edge_target_later,
            self.test_validate_backward_edge_missing_fields,
            self.test_validate_backward_edge_cap_exceeded,
            self.test_post_flight_pass,
            self.test_post_flight_wrong_artifact,
            self.test_post_flight_dirty_source_mutation,
            self.test_non_git_snapshot_preserves_existing_artifacts,
            self.test_post_flight_existing_foreign_artifact_mutation,
            self.test_post_flight_existing_foreign_artifact_deletion,
            self.test_post_flight_manifest_mutation,
            self.test_commit_record_must_match_new_head,
            self.test_loop_cap_uses_revision_suffixes,
            self.test_loop_cap_ignores_other_phase_revisions,
            self.test_checker_must_follow_doer,
        ]

        for test in tests:
            try:
                test()
            except Exception as e:
                self.failed += 1
                print(f"  FAIL: {test.__name__} raised exception: {e}")

        print("\n" + "=" * 60)
        print(f"Results: {self.passed} passed, {self.failed} failed")
        print("=" * 60)
        return 1 if self.failed else 0


def main() -> int:
    test = DryRunTest()
    try:
        return test.run_all()
    finally:
        test.cleanup()


if __name__ == "__main__":
    raise SystemExit(main())
