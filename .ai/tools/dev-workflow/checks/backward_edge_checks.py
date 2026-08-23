"""Category 4: Backward edge checks.

Verify that backward handoff packets have all required fields, target an
earlier phase, and respect the backward edge cap of 2.
"""

from __future__ import annotations

import re
from pathlib import Path

from . import Finding

REQUIRED_PACKET_FIELDS = [
    "# Backward Handoff Packet",
    "## Routing",
    "From phase:",
    "To phase:",
    "Backward edge count for target phase:",
    "## Source finding",
    "Finding id:",
    "Severity:",
    "## Root cause classification",
    "## What the target phase must resolve",
    "## Context from the source phase",
]

# Phase ordering for backward edge validation.
# A backward edge must go to an earlier phase.
PHASE_ORDER = ["clarify", "research", "plan", "implement", "code-review", "commit"]

# Valid phases for root-cause-phase routing.
VALID_TARGET_PHASES = {"clarify", "research", "plan", "implement", "code-review"}

# Backward edge cap per phase.
BACKWARD_EDGE_CAP = 2


def check_packet_fields(run_dir: Path, packet_path: Path) -> list[Finding]:
    """Check that a backward handoff packet has all required fields."""
    findings: list[Finding] = []
    if not packet_path.exists():
        return [Finding(
            severity="error",
            check="backward_edge",
            message=f"Backward handoff packet not found: {packet_path.name}",
        )]

    text = packet_path.read_text(encoding="utf-8")
    for field in REQUIRED_PACKET_FIELDS:
        if field not in text:
            findings.append(Finding(
                severity="error",
                check="backward_edge",
                message=f"Backward packet {packet_path.name} missing field: {field}",
            ))
    return findings


def check_target_is_earlier(run_dir: Path, packet_path: Path) -> list[Finding]:
    """Check that the target phase is earlier than the source phase."""
    findings: list[Finding] = []
    if not packet_path.exists():
        return []

    text = packet_path.read_text(encoding="utf-8")

    from_match = re.search(r"From phase:\s*(\S+)", text, re.IGNORECASE)
    to_match = re.search(r"To phase:\s*(\S+)", text, re.IGNORECASE)

    if not from_match or not to_match:
        findings.append(Finding(
            severity="error",
            check="backward_edge",
            message=f"Backward packet {packet_path.name} missing from/to phase",
        ))
        return findings

    from_phase = from_match.group(1).strip().lower()
    to_phase = to_match.group(1).strip().lower()

    if from_phase not in PHASE_ORDER or to_phase not in PHASE_ORDER:
        findings.append(Finding(
            severity="error",
            check="backward_edge",
            message=(
                f"Backward packet {packet_path.name} has invalid phase: "
                f"from={from_phase}, to={to_phase}"
            ),
        ))
        return findings

    from_idx = PHASE_ORDER.index(from_phase)
    to_idx = PHASE_ORDER.index(to_phase)

    if to_idx >= from_idx:
        findings.append(Finding(
            severity="error",
            check="backward_edge",
            message=(
                f"Backward packet {packet_path.name} targets a later or same phase: "
                f"from={from_phase}, to={to_phase}"
            ),
        ))
    return findings


def check_backward_edge_cap(run_dir: Path, packet_path: Path) -> list[Finding]:
    """Check that the backward edge count for the target phase is within cap."""
    findings: list[Finding] = []
    if not packet_path.exists():
        return []

    text = packet_path.read_text(encoding="utf-8")
    count_match = re.search(
        r"Backward edge count for target phase:\s*(\d+)\s*of\s*2",
        text, re.IGNORECASE,
    )
    if count_match:
        count = int(count_match.group(1))
        if count > BACKWARD_EDGE_CAP:
            findings.append(Finding(
                severity="error",
                check="backward_edge",
                message=(
                    f"Backward edge cap exceeded in {packet_path.name}: "
                    f"{count} > {BACKWARD_EDGE_CAP}"
                ),
            ))
    return findings


def run_all(run_dir: Path, packet_path: Path) -> list[Finding]:
    """Run all backward edge checks on a single packet.

    Finding-id reference validation is owned by handoff_checks
    (check_backward_packet_finding_exists) to avoid duplicate findings when
    validate_backward_edge.py runs both modules.
    """
    findings: list[Finding] = []
    findings.extend(check_packet_fields(run_dir, packet_path))
    findings.extend(check_target_is_earlier(run_dir, packet_path))
    findings.extend(check_backward_edge_cap(run_dir, packet_path))
    return findings
