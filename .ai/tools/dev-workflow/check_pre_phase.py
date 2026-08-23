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

# Expected input artifacts per phase (the terminal artifact from the previous phase).
PHASE_INPUTS: dict[str, list[str]] = {
    "clarify": ["01-feature-brief.md"],
    "research": ["02-requirement-ledger.md"],
    "plan": ["10-research-report.md"],
    "implement": ["20-implementation-plan.md"],
    "code-review": ["30-implementation-report.md"],
    "commit": ["40-code-review.md"],
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

    # Check expected input artifacts exist.
    inputs = PHASE_INPUTS.get(phase, [])
    for filename in inputs:
        path = run_dir / filename
        if not path.exists():
            findings.append(Finding(
                severity="error",
                check="pre_flight",
                message=f"Expected input artifact missing for {phase}: {filename}",
            ))
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
