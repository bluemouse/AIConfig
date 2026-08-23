#!/usr/bin/env python3
"""Post-flight check: verify only allowed artifacts were written after a phase step.

Checks that:
- Only artifacts with allowed prefixes were created/modified in the run dir
- No forbidden files were touched (source in read-only phases)
- The manifest is still valid after the phase step

Usage:
    python tools/dev-workflow/check_post_phase.py --phase research --run-dir .ai/workflow/<slug> [--repo-root <path>]

Exit codes:
    0 — post-flight checks passed
    1 — one or more errors found
    2 — usage error or missing run directory
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from checks import Finding
from checks import mode_checks
from checks import manifest_checks


def run_post_flight(run_dir: Path, phase: str, repo_root: Path | None = None) -> list[Finding]:
    """Run post-flight checks after a phase step.

    Post-flight checks are a lightweight subset of validation:
    - Mode enforcement: only allowed artifacts written, no forbidden source edits,
      no commits in non-commit phases. (Uses the baseline to distinguish
      pre-existing changes from phase changes.)
    - Manifest still exists and has required sections.

    Content checks (artifact sections, verdicts, handoff integrity) are NOT
    run here — they are run by validate_phase.py after the loop exits.
    """
    findings: list[Finding] = []
    # Mode enforcement: only allowed artifacts written, no forbidden source edits.
    findings.extend(mode_checks.run_all(run_dir, phase, repo_root))
    # Manifest still exists and is structurally valid.
    findings.extend(manifest_checks.check_manifest_exists(run_dir))
    findings.extend(manifest_checks.check_manifest_sections(run_dir))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Post-flight check after a dev-workflow phase step."
    )
    parser.add_argument(
        "--phase",
        required=True,
        choices=["clarify", "research", "plan", "implement", "code-review", "commit"],
        help="The phase that just ran.",
    )
    parser.add_argument(
        "--run-dir",
        required=True,
        type=Path,
        help="Path to the run directory.",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Path to the git repository root (for source-edit checks).",
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

    findings = run_post_flight(run_dir, args.phase, repo_root)

    errors = [f for f in findings if f.severity == "error"]
    warnings = [f for f in findings if f.severity == "warning"]

    if errors:
        print(f"POST-FLIGHT CHECK FAILED ({args.phase})")
        for f in errors:
            print(f"  ERROR: {f.check}: {f.message}")
    else:
        print(f"POST-FLIGHT CHECK PASSED ({args.phase})")

    if warnings:
        print("WARNINGS")
        for f in warnings:
            print(f"  WARNING: {f.check}: {f.message}")

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
