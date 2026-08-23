#!/usr/bin/env python3
"""Validate a dev-workflow phase after its loop exits.

Runs all check categories (artifact structure, manifest state, loop contract,
mode enforcement, handoff integrity) for the specified phase and reports
findings with severity (error/warning).

Usage:
    python .ai/tools/dev-workflow/validate_phase.py --phase research --run-dir .ai/workflow/<slug>

Exit codes:
    0 — no errors (warnings may be present)
    1 — one or more errors found
    2 — usage error or missing run directory
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow importing checks/ whether run as a script or module.
sys.path.insert(0, str(Path(__file__).parent))

from checks import Finding
from checks import artifact_checks
from checks import manifest_checks
from checks import loop_checks
from checks import mode_checks
from checks import handoff_checks


def run_phase_validation(run_dir: Path, phase: str, repo_root: Path | None = None) -> list[Finding]:
    """Run all validation checks for a phase. Returns a list of findings."""
    findings: list[Finding] = []
    findings.extend(artifact_checks.run_all(run_dir, phase))
    findings.extend(manifest_checks.run_all(run_dir, phase))
    findings.extend(loop_checks.run_all(run_dir, phase))
    findings.extend(mode_checks.run_all(run_dir, phase, repo_root))
    findings.extend(handoff_checks.run_all(run_dir, phase))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate a dev-workflow phase after its loop exits."
    )
    parser.add_argument(
        "--phase",
        required=True,
        choices=["clarify", "research", "plan", "implement", "code-review", "commit"],
        help="The phase to validate.",
    )
    parser.add_argument(
        "--run-dir",
        required=True,
        type=Path,
        help="Path to the run directory (e.g., .ai/workflow/<slug>).",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Path to the git repository root (for mode enforcement checks). "
             "Defaults to the first parent of run-dir containing .git.",
    )
    args = parser.parse_args()

    run_dir = args.run_dir.resolve()
    if not run_dir.is_dir():
        print(f"ERROR: run directory not found: {run_dir}")
        return 2

    # Find repo root if not specified.
    repo_root = args.repo_root
    if repo_root is None:
        current = run_dir
        while current != current.parent:
            if (current / ".git").exists():
                repo_root = current
                break
            current = current.parent

    findings = run_phase_validation(run_dir, args.phase, repo_root)

    errors = [f for f in findings if f.severity == "error"]
    warnings = [f for f in findings if f.severity == "warning"]

    if errors:
        print(f"PHASE VALIDATION FAILED ({args.phase})")
        for f in errors:
            print(f"  ERROR: {f.check}: {f.message}")
    else:
        print(f"PHASE VALIDATION PASSED ({args.phase})")

    if warnings:
        print("WARNINGS")
        for f in warnings:
            print(f"  WARNING: {f.check}: {f.message}")

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
