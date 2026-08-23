"""Category 6: Handoff integrity checks.

Verify that forward handoffs have consumer-ready artifacts and that backward
handoff packets reference real finding ids from the source review.
"""

from __future__ import annotations

import re
from pathlib import Path

from . import Finding

# Required sections in the research report for plan-guide to consume.
RESEARCH_REPORT_FOR_PLAN = [
    "## Problem statement",
    "## Goals",
    "## Requirements",
]

# Required sections in the implementation plan for plan-executor to consume.
PLAN_FOR_EXECUTOR = [
    "## Planning status",
    "## Task breakdown",
]

# Required sections in the implementation report for code-reviewer to consume.
IMPL_REPORT_FOR_REVIEW = [
    "# Implementation Report",
    "## Files changed",
]


def check_research_report_consumer_ready(run_dir: Path) -> list[Finding]:
    """Check that the research report has sections plan-guide needs."""
    findings: list[Finding] = []
    path = run_dir / "10-research-report.md"
    if not path.exists():
        return []  # Already reported by artifact_checks
    text = path.read_text(encoding="utf-8")
    for section in RESEARCH_REPORT_FOR_PLAN:
        if section not in text:
            findings.append(Finding(
                severity="error",
                check="handoff_integrity",
                message=(
                    f"Research report missing section for plan-guide consumption: {section}"
                ),
            ))
    return findings


def check_plan_consumer_ready(run_dir: Path) -> list[Finding]:
    """Check that the implementation plan has sections plan-executor needs."""
    findings: list[Finding] = []
    path = run_dir / "20-implementation-plan.md"
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    for section in PLAN_FOR_EXECUTOR:
        if section not in text:
            findings.append(Finding(
                severity="error",
                check="handoff_integrity",
                message=(
                    f"Implementation plan missing section for plan-executor consumption: {section}"
                ),
            ))
    return findings


def check_impl_report_consumer_ready(run_dir: Path) -> list[Finding]:
    """Check that the implementation report has sections code-reviewer needs."""
    findings: list[Finding] = []
    path = run_dir / "30-implementation-report.md"
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    for section in IMPL_REPORT_FOR_REVIEW:
        if section not in text:
            findings.append(Finding(
                severity="error",
                check="handoff_integrity",
                message=(
                    f"Implementation report missing section for code-reviewer consumption: {section}"
                ),
            ))
    return findings


def check_backward_packet_finding_exists(run_dir: Path, packet_path: Path) -> list[Finding]:
    """Check that a backward packet's finding id exists in the source artifact."""
    findings: list[Finding] = []
    if not packet_path.exists():
        return []

    text = packet_path.read_text(encoding="utf-8")
    finding_match = re.search(r"Finding id:\s*(\S+)", text, re.IGNORECASE)
    if not finding_match:
        return []  # Already reported by backward_edge_checks

    finding_id = finding_match.group(1).strip().lower()

    # Determine source artifact from packet filename.
    name = packet_path.name.lower()
    source_artifact = None
    if name.startswith("back-review"):
        source_artifact = "40-code-review.md"
    elif name.startswith("back-impl"):
        source_artifact = "31-implementation-audit.md"
    elif name.startswith("back-plan"):
        source_artifact = "21-plan-review.md"

    if source_artifact is None:
        return []

    source_path = run_dir / source_artifact
    if not source_path.exists():
        return []

    source_text = source_path.read_text(encoding="utf-8")
    if finding_id not in source_text.lower():
        findings.append(Finding(
            severity="error",
            check="handoff_integrity",
            message=(
                f"Backward packet {packet_path.name} references finding id "
                f"{finding_id} not found in {source_artifact}"
            ),
        ))
    return findings


def run_all(run_dir: Path, phase: str) -> list[Finding]:
    """Run handoff integrity checks for a phase's forward handoff."""
    findings: list[Finding] = []
    if phase == "research":
        findings.extend(check_research_report_consumer_ready(run_dir))
    elif phase == "plan":
        findings.extend(check_plan_consumer_ready(run_dir))
    elif phase == "implement":
        findings.extend(check_impl_report_consumer_ready(run_dir))
    return findings
