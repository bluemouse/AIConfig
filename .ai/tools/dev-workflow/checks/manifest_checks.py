"""Category 2: Manifest state checks.

Verify that the run manifest is valid, parseable, and consistent with the
artifacts that exist on disk.
"""

from __future__ import annotations

import re
from pathlib import Path

from . import Finding

MANIFEST_FILENAME = "00-run-manifest.md"

REQUIRED_MANIFEST_SECTIONS = [
    "# Run Manifest",
    "## Run metadata",
    "## Phase status",
    "## Artifact registry",
]

VALID_PHASES = {"clarify", "research", "plan", "implement", "code-review", "commit", "done"}
VALID_RUN_STATUSES = {"in-progress", "completed", "blocked", "abandoned"}
VALID_RUN_MODES = {"linear", "staged"}
VALID_PHASE_STATUSES = {
    "not-started", "in-progress", "loop-active", "accepted",
    "backward-edge-received", "completed",
}


def _read_manifest(run_dir: Path) -> str | None:
    """Read the manifest file, returning None if it doesn't exist."""
    path = run_dir / MANIFEST_FILENAME
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def check_manifest_exists(run_dir: Path) -> list[Finding]:
    """Check that the manifest file exists."""
    path = run_dir / MANIFEST_FILENAME
    if not path.exists():
        return [Finding(
            severity="error",
            check="manifest_state",
            message=f"Run manifest missing: {MANIFEST_FILENAME}",
        )]
    return []


def check_manifest_sections(run_dir: Path) -> list[Finding]:
    """Check that the manifest has all required sections."""
    findings: list[Finding] = []
    text = _read_manifest(run_dir)
    if text is None:
        return []  # Already reported by check_manifest_exists
    for section in REQUIRED_MANIFEST_SECTIONS:
        if section not in text:
            findings.append(Finding(
                severity="error",
                check="manifest_state",
                message=f"Manifest missing required section: {section}",
            ))
    return findings


def check_current_phase_valid(run_dir: Path) -> list[Finding]:
    """Check that the current phase field is present and valid."""
    findings: list[Finding] = []
    text = _read_manifest(run_dir)
    if text is None:
        return []
    match = re.search(r"Current phase:\s*(\S+)", text)
    if not match:
        findings.append(Finding(
            severity="error",
            check="manifest_state",
            message="Manifest missing 'Current phase' field",
        ))
    elif match.group(1).lower() not in VALID_PHASES:
        findings.append(Finding(
            severity="error",
            check="manifest_state",
            message=f"Invalid current phase: {match.group(1)}",
        ))
    return findings


def check_run_status_valid(run_dir: Path) -> list[Finding]:
    """Check that the run status field is present and valid."""
    findings: list[Finding] = []
    text = _read_manifest(run_dir)
    if text is None:
        return []
    match = re.search(r"Run status:\s*(\S+)", text)
    if not match:
        findings.append(Finding(
            severity="error",
            check="manifest_state",
            message="Manifest missing 'Run status' field",
        ))
    elif match.group(1).lower() not in VALID_RUN_STATUSES:
        findings.append(Finding(
            severity="error",
            check="manifest_state",
            message=f"Invalid run status: {match.group(1)}",
        ))
    return findings


def check_run_mode_valid(run_dir: Path) -> list[Finding]:
    """Check that the Run mode field, if present, is valid.

    Run mode is optional — if absent, it defaults to linear. If present,
    it must be one of VALID_RUN_MODES (linear or staged).
    """
    findings: list[Finding] = []
    text = _read_manifest(run_dir)
    if text is None:
        return []
    match = re.search(r"Run mode:\s*(\S+)", text)
    if match and match.group(1).lower() not in VALID_RUN_MODES:
        findings.append(Finding(
            severity="error",
            check="manifest_state",
            message=f"Invalid run mode: {match.group(1)}. Expected one of: {', '.join(sorted(VALID_RUN_MODES))}",
        ))
    return findings


def check_backward_edge_counts(run_dir: Path) -> list[Finding]:
    """Check that backward edge counts in the manifest match the back-*.md files on disk."""
    findings: list[Finding] = []
    text = _read_manifest(run_dir)
    if text is None:
        return []

    # Count actual backward handoff packet files per target phase
    disk_counts: dict[str, int] = {}
    for path in run_dir.iterdir():
        if not path.is_file() or not path.name.startswith("back-"):
            continue
        # Filename format: back-<from>-to-<to>-<n>.md
        parts = path.name.removesuffix(".md").split("-")
        if len(parts) >= 4 and parts[1] == "to":
            target = parts[2]
            disk_counts[target] = disk_counts.get(target, 0) + 1

    # Check manifest backward edge counts
    for phase in ("clarify", "research", "plan", "implement", "code-review"):
        match = re.search(
            rf"### Phase.*{phase}.*\n.*Backward edges received:\s*(\d+)",
            text, re.IGNORECASE | re.DOTALL,
        )
        if match:
            manifest_count = int(match.group(1))
            disk_count = disk_counts.get(phase, 0)
            if manifest_count != disk_count:
                findings.append(Finding(
                    severity="error",
                    check="manifest_state",
                    message=(
                        f"Backward edge count mismatch for {phase}: "
                        f"manifest={manifest_count}, disk={disk_count}"
                    ),
                ))
            if manifest_count > 2:
                findings.append(Finding(
                    severity="error",
                    check="manifest_state",
                    message=(
                        f"Backward edge cap exceeded for {phase}: "
                        f"{manifest_count} > 2"
                    ),
                ))
    return findings


def run_all(run_dir: Path, phase: str) -> list[Finding]:
    """Run all manifest state checks."""
    findings: list[Finding] = []
    findings.extend(check_manifest_exists(run_dir))
    findings.extend(check_manifest_sections(run_dir))
    findings.extend(check_current_phase_valid(run_dir))
    findings.extend(check_run_status_valid(run_dir))
    findings.extend(check_run_mode_valid(run_dir))
    findings.extend(check_backward_edge_counts(run_dir))
    return findings
