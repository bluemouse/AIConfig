#!/usr/bin/env python3
"""Validate a backward handoff packet.

Checks that the packet has all required fields, targets an earlier phase,
respects the backward edge cap, and references a real finding id.

Usage:
    python .ai/tools/dev-workflow/validate_backward_edge.py --packet <path> [--run-dir <path>]

Exit codes:
    0 — no errors (warnings may be present)
    1 — one or more errors found
    2 — usage error or missing packet file
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from checks import Finding
from checks import backward_edge_checks
from checks import handoff_checks


def run_backward_edge_validation(run_dir: Path, packet_path: Path) -> list[Finding]:
    """Run all validation checks for a backward handoff packet."""
    findings: list[Finding] = []
    findings.extend(backward_edge_checks.run_all(run_dir, packet_path))
    findings.extend(handoff_checks.check_backward_packet_finding_exists(run_dir, packet_path))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate a backward handoff packet."
    )
    parser.add_argument(
        "--packet",
        required=True,
        type=Path,
        help="Path to the backward handoff packet file.",
    )
    parser.add_argument(
        "--run-dir",
        required=True,
        type=Path,
        help="Path to the run directory (e.g., .ai/workflow/<slug>).",
    )
    args = parser.parse_args()

    packet_path = args.packet.resolve()
    run_dir = args.run_dir.resolve()

    if not run_dir.is_dir():
        print(f"ERROR: run directory not found: {run_dir}")
        return 2

    findings = run_backward_edge_validation(run_dir, packet_path)

    errors = [f for f in findings if f.severity == "error"]
    warnings = [f for f in findings if f.severity == "warning"]

    if errors:
        print(f"BACKWARD EDGE VALIDATION FAILED ({packet_path.name})")
        for f in errors:
            print(f"  ERROR: {f.check}: {f.message}")
    else:
        print(f"BACKWARD EDGE VALIDATION PASSED ({packet_path.name})")

    if warnings:
        print("WARNINGS")
        for f in warnings:
            print(f"  WARNING: {f.check}: {f.message}")

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
