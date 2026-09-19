#!/usr/bin/env python3
"""Pre-flight check: verify working tree state before a phase starts.

Checks that:
- The run directory exists
- The manifest is present and readable
- Expected input artifacts from the previous phase exist
- No unexpected dirty files overlap with the phase's scope

Usage:
    python .ai/tools/dev-workflow/check_pre_phase.py --phase plan --run-dir .ai/workflow/<slug>

Exit codes:
    0 — pre-flight checks passed
    1 — one or more errors found
    2 — usage error or missing run directory
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from checks import Finding
from checks import artifact_checks
from checks import handoff_checks

# Expected input artifacts per phase (the terminal artifact from the previous phase).
# In staged mode, stage-indexed variants (e.g. 30-stage1-implementation-report.md)
# or the final deep review (40-final-deep-review.md) satisfy these requirements.
PHASE_INPUTS: dict[str, list[str]] = {
    "clarify": ["01-feature-brief.md"],
    "research": ["02-requirement-ledger.md"],
    "plan": ["10-research-report.md"],
    "implement": ["20-implementation-plan.md"],
    "code-review": ["30-implementation-report.md"],
    "commit": ["40-code-review.md"],
}

# Handoff consumer-ready checks to run at pre-flight, keyed by the phase whose
# INPUT is being consumed. A phase cannot start on an input artifact that is
# missing sections its consumer needs (dw-016: pre-flight was existence-only,
# so a research report or plan missing required sections passed pre-flight and
# surfaced only post-hoc in validate_phase).
PRE_FLIGHT_HANDOFF_CHECKS: dict[str, list] = {
    "plan": [handoff_checks.check_research_report_consumer_ready],
    "implement": [handoff_checks.check_plan_consumer_ready],
    "code-review": [handoff_checks.check_impl_report_consumer_ready],
}


def run_pre_flight(run_dir: Path, phase: str) -> list[Finding]:
    """Run pre-flight checks before a phase starts."""
    findings: list[Finding] = []

    # Check run directory exists.
    if not run_dir.is_dir():
        findings.append(Finding(
            severity="error",
            check="pre_flight",
            message=f"Run directory not found: {run_dir}",
        ))
        return findings

    # Check manifest exists.
    manifest = run_dir / "00-run-manifest.md"
    if not manifest.exists():
        findings.append(Finding(
            severity="error",
            check="pre_flight",
            message="Run manifest missing: 00-run-manifest.md",
        ))

    # Check expected input artifacts exist. In staged mode, stage-indexed
    # variants (or the final deep review for the commit phase) are accepted.
    staged_mode = artifact_checks._is_staged_mode(run_dir)
    inputs = PHASE_INPUTS.get(phase, [])
    for filename in inputs:
        if staged_mode:
            resolved = artifact_checks._resolve_artifact_path(
                run_dir, filename, phase, staged_mode
            )
            # For the commit phase in staged mode, the final deep review
            # (40-final-deep-review.md) also satisfies the 40-code-review.md input.
            if resolved is None and filename == "40-code-review.md":
                final_path = run_dir / "40-final-deep-review.md"
                if final_path.exists():
                    continue
            if resolved is not None:
                continue
        else:
            if (run_dir / filename).exists():
                continue
        findings.append(Finding(
            severity="error",
            check="pre_flight",
            message=f"Expected input artifact missing for {phase}: {filename}",
        ))

    # Handoff consumer-ready checks: the input artifact must contain the
    # sections its consumer needs, not merely exist (dw-016).
    for check in PRE_FLIGHT_HANDOFF_CHECKS.get(phase, []):
        findings.extend(check(run_dir))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Pre-flight check before a dev-workflow phase starts."
    )
    parser.add_argument(
        "--phase",
        required=True,
        choices=["clarify", "research", "plan", "implement", "code-review", "commit"],
        help="The phase about to start.",
    )
    parser.add_argument(
        "--run-dir",
        required=True,
        type=Path,
        help="Path to the run directory.",
    )
    args = parser.parse_args()

    run_dir = args.run_dir.resolve()
    findings = run_pre_flight(run_dir, args.phase)

    errors = [f for f in findings if f.severity == "error"]
    warnings = [f for f in findings if f.severity == "warning"]

    if errors:
        print(f"PRE-FLIGHT CHECK FAILED ({args.phase})")
        for f in errors:
            print(f"  ERROR: {f.check}: {f.message}")
    else:
        print(f"PRE-FLIGHT CHECK PASSED ({args.phase})")

    if warnings:
        print("WARNINGS")
        for f in warnings:
            print(f"  WARNING: {f.check}: {f.message}")

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
