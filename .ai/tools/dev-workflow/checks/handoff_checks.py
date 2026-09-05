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
    # Resolve the implementation report path, including stage-indexed variants
    # in staged mode (e.g. 30-stage1-implementation-report.md).
    from . import artifact_checks
    staged = artifact_checks._is_staged_mode(run_dir)
    path = artifact_checks._resolve_artifact_path(
        run_dir, "30-implementation-report.md", "implement", staged
    )
    if path is None:
        return []  # Already reported by artifact_checks
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

    # Determine the source artifact. Prefer the packet's own "Source artifact:"
    # field (authoritative); fall back to inferring from the filename prefix
    # for packets that don't declare it.
    source_artifact = None
    source_match = re.search(r"Source artifact:\s*(\S+)", text, re.IGNORECASE)
    if source_match:
        source_artifact = source_match.group(1).strip()

    if source_artifact is None:
        # Fallback: infer from the packet filename prefix.
        name = packet_path.name.lower()
        if name.startswith("back-code-review") or name.startswith("back-review"):
            source_artifact = "40-code-review.md"
        elif name.startswith("back-implement") or name.startswith("back-impl"):
            source_artifact = "31-implementation-audit.md"
        elif name.startswith("back-plan"):
            source_artifact = "21-plan-review.md"
        elif name.startswith("back-research"):
            source_artifact = "11-research-review.md"

    if source_artifact is None:
        return []

    # Resolve the source artifact path, including stage-indexed variants and
    # staged-mode "final" aliases (e.g. 40-final-deep-review.md) so a packet
    # declaring the canonical name still finds a stage-indexed source on disk.
    from . import artifact_checks
    staged = artifact_checks._is_staged_mode(run_dir)
    source_path = artifact_checks._resolve_artifact_path(
        run_dir, source_artifact, "code-review", staged
    )
    if source_path is None:
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
