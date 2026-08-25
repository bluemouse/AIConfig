"""Category 1: Artifact structure checks.

Verify that expected artifacts exist at expected paths and contain required sections.
"""

from __future__ import annotations

import re
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

# Phases that support stage-indexed artifacts in staged mode.
# Maps a phase to the set of artifact prefixes that can have stage-indexed variants.
# For example, "implement" phase has artifacts with prefixes 30, 31, 32, 33.
# In staged mode, 30-stage1-implementation-report.md satisfies the 30-implementation-report.md requirement.
STAGED_PHASE_PREFIXES: dict[str, set[str]] = {
    "implement": {"30", "31", "32", "33"},
    "code-review": {"40", "41", "42", "43"},
}

# Regex to extract the stage number from a stage-indexed filename.
# Matches patterns like 30-stage1-implementation-report.md, 31-stage2-implementation-audit.md, etc.
_STAGE_INDEX_RE = re.compile(r"^(\d{2})-stage(\d+)-(.+\.md)$")


def _is_staged_mode(run_dir: Path) -> bool:
    """Check whether the run is in staged mode by reading the manifest.

    Returns True if the manifest has `Run mode: staged`, False otherwise
    (including when the manifest is missing or the field is absent).
    Uses regex to match the exact field value, not a fragile substring match.
    """
    manifest_path = run_dir / "00-run-manifest.md"
    if not manifest_path.exists():
        return False
    text = manifest_path.read_text(encoding="utf-8")
    match = re.search(r"Run mode:\s*(\S+)", text)
    if match:
        return match.group(1) == "staged"
    return False


def _find_stage_indexed_artifact(
    run_dir: Path, expected_filename: str, phase: str
) -> Path | None:
    """Find a stage-indexed variant of an expected artifact.

    In staged mode, 30-stage1-implementation-report.md satisfies the
    30-implementation-report.md requirement. This function searches the run
    directory for a stage-indexed file matching the expected filename's
    prefix and suffix.

    Returns the path to the stage-indexed file if found, None otherwise.
    """
    # Extract the prefix (e.g., "30") and the suffix (e.g., "implementation-report.md")
    # from the expected filename (e.g., "30-implementation-report.md").
    if len(expected_filename) < 3 or expected_filename[2] != "-":
        return None
    prefix = expected_filename[:2]
    suffix = expected_filename[3:]  # e.g., "implementation-report.md"

    # Check if this phase supports stage-indexed variants for this prefix
    allowed_prefixes = STAGED_PHASE_PREFIXES.get(phase, set())
    if prefix not in allowed_prefixes:
        return None

    # Search for a file matching {prefix}-stage{N}-{suffix}
    for path in run_dir.iterdir():
        if not path.is_file() or not path.name.endswith(".md"):
            continue
        match = _STAGE_INDEX_RE.match(path.name)
        if match:
            file_prefix = match.group(1)
            file_suffix = match.group(3)
            if file_prefix == prefix and file_suffix == suffix:
                return path

    return None


def check_artifacts_exist(run_dir: Path, phase: str) -> list[Finding]:
    """Check that all expected artifacts for a phase exist.

    In staged mode (manifest has `Run mode: staged`), stage-indexed variants
    (e.g., 30-stage1-implementation-report.md) are accepted in place of the
    exact filename (e.g., 30-implementation-report.md) for phases that support
    stage-indexed artifacts.
    """
    findings: list[Finding] = []
    artifacts = PHASE_ARTIFACTS.get(phase, [])
    staged_mode = _is_staged_mode(run_dir)
    for filename, _sections in artifacts:
        path = run_dir / filename
        if path.exists():
            continue  # Exact filename found — done
        if staged_mode:
            # Try to find a stage-indexed variant
            stage_path = _find_stage_indexed_artifact(run_dir, filename, phase)
            if stage_path is not None:
                continue  # Stage-indexed variant found
        findings.append(
            Finding(
                severity="error",
                check="artifact_structure",
                message=f"Required artifact missing: {filename}",
            )
        )
    return findings


def check_artifact_sections(run_dir: Path, phase: str) -> list[Finding]:
    """Check that existing artifacts contain required sections.

    In staged mode, stage-indexed variants are checked for required sections
    when the exact filename is not present.
    """
    findings: list[Finding] = []
    artifacts = PHASE_ARTIFACTS.get(phase, [])
    staged_mode = _is_staged_mode(run_dir)
    for filename, required_sections in artifacts:
        path = run_dir / filename
        if not path.exists():
            if staged_mode:
                # Try to find a stage-indexed variant
                stage_path = _find_stage_indexed_artifact(run_dir, filename, phase)
                if stage_path is not None:
                    path = stage_path
                else:
                    continue  # Already reported by check_artifacts_exist
            else:
                continue  # Already reported by check_artifacts_exist
        text = path.read_text(encoding="utf-8")
        for section in required_sections:
            if section not in text:
                findings.append(
                    Finding(
                        severity="error",
                        check="artifact_structure",
                        message=f"Required section missing in {path.name}: {section}",
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
