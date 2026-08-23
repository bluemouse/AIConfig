"""Category 1: Artifact structure checks.

Verify that expected artifacts exist at expected paths and contain required sections.
"""

from __future__ import annotations

from pathlib import Path

from . import Finding

# Expected artifacts per phase. Keyed by phase name.
# Each entry: (filename, required_sections) where required_sections is a list
# of markdown headings that must appear in the file.
PHASE_ARTIFACTS: dict[str, list[tuple[str, list[str]]]] = {
    "clarify": [
        ("02-requirement-ledger.md", ["# Requirement Ledger", "## Outcome", "## Scope", "## Acceptance criteria", "## Assumptions"]),
    ],
    "research": [
        ("10-research-report.md", ["# Research Report", "## Problem statement"]),
        ("11-research-review.md", ["## Verdict"]),
    ],
    "plan": [
        ("20-implementation-plan.md", ["# Implementation Plan", "## Planning status"]),
        ("21-plan-review.md", ["## Verdict"]),
    ],
    "implement": [
        ("30-implementation-report.md", ["# Implementation Report"]),
        ("31-implementation-audit.md", ["## Verdict"]),
    ],
    "code-review": [
        ("40-code-review.md", ["# Code Review Report"]),
        ("41-fix-report.md", ["# Fix Report", "## Summary"]),
    ],
    "commit": [
        ("50-commit.md", ["# Commit Record"]),
    ],
}


def check_artifacts_exist(run_dir: Path, phase: str) -> list[Finding]:
    """Check that all expected artifacts for a phase exist."""
    findings: list[Finding] = []
    artifacts = PHASE_ARTIFACTS.get(phase, [])
    for filename, _sections in artifacts:
        path = run_dir / filename
        if not path.exists():
            findings.append(
                Finding(
                    severity="error",
                    check="artifact_structure",
                    message=f"Required artifact missing: {filename}",
                )
            )
    return findings


def check_artifact_sections(run_dir: Path, phase: str) -> list[Finding]:
    """Check that existing artifacts contain required sections."""
    findings: list[Finding] = []
    artifacts = PHASE_ARTIFACTS.get(phase, [])
    for filename, required_sections in artifacts:
        path = run_dir / filename
        if not path.exists():
            continue  # Already reported by check_artifacts_exist
        text = path.read_text(encoding="utf-8")
        for section in required_sections:
            if section not in text:
                findings.append(
                    Finding(
                        severity="error",
                        check="artifact_structure",
                        message=f"Required section missing in {filename}: {section}",
                    )
                )
    return findings


def check_artifact_naming(run_dir: Path) -> list[Finding]:
    """Check that artifact filenames follow the phase-grouped numbering scheme."""
    findings: list[Finding] = []
    valid_prefixes = {"00", "01", "02", "10", "11", "12", "13", "14", "15", "20", "21", "22", "23",
                      "30", "31", "32", "33", "40", "41", "42", "43", "50"}
    for path in run_dir.iterdir():
        if not path.is_file() or not path.name.endswith(".md"):
            continue
        if path.name.startswith("back-"):
            continue  # Backward handoff packets validated separately
        prefix = path.name[:2]
        if prefix not in valid_prefixes:
            findings.append(
                Finding(
                    severity="warning",
                    check="artifact_structure",
                    message=f"Filename does not match phase-grouped numbering: {path.name}",
                )
            )
    return findings


def run_all(run_dir: Path, phase: str) -> list[Finding]:
    """Run all artifact structure checks for a phase."""
    findings: list[Finding] = []
    findings.extend(check_artifacts_exist(run_dir, phase))
    findings.extend(check_artifact_sections(run_dir, phase))
    findings.extend(check_artifact_naming(run_dir))
    return findings
