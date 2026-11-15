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


def _parse_backward_edge_counts_from_manifest(text: str) -> dict[str, int]:
    """Parse per-phase backward edge counts from the manifest.

    The manifest uses ``### Phase N: <Name>`` section headers followed by a
    ``- Backward edges received: <n>`` line. Phase names in the manifest use
    display forms ("Code Review") that must be mapped to phase ids
    ("code-review"). This function splits the manifest into sections and
    extracts each section's count, so a greedy regex cannot misattribute one
    phase's count to another.
    """
    # Map display-name fragments (as they appear in "### Phase N: <Name>")
    # to canonical phase ids used elsewhere in the checks.
    display_to_id = {
        "clarify": "clarify",
        "research": "research",
        "plan": "plan",
        "implement": "implement",
        "code review": "code-review",
        "code-review": "code-review",
    }
    counts: dict[str, int] = {}
    # Split on "### " headers; each chunk starts with the header line.
    for chunk in re.split(r"(?=^###\s+Phase\b)", text, flags=re.MULTILINE):
        header_match = re.match(r"^###\s+Phase\s+\d+:\s*(.+?)\s*$", chunk, re.MULTILINE)
        if not header_match:
            continue
        display_name = header_match.group(1).strip().lower()
        phase_id = display_to_id.get(display_name)
        if phase_id is None:
            # Fall back to substring matching for robustness.
            for key, pid in display_to_id.items():
                if key in display_name:
                    phase_id = pid
                    break
        if phase_id is None:
            continue
        count_match = re.search(
            r"Backward edges received:\s*(\d+)", chunk, re.IGNORECASE
        )
        if count_match:
            counts[phase_id] = int(count_match.group(1))
    return counts


def _parse_backward_edge_counts_from_disk(run_dir: Path) -> dict[str, int]:
    """Count backward handoff packet files per target phase on disk.

    Packet filename format: ``back-<from>-to-<to>-<n>.md`` where ``<from>``
    and ``<to>`` are phase names (e.g. ``back-implement-to-plan-1.md``).
    """
    counts: dict[str, int] = {}
    for path in run_dir.iterdir():
        if not path.is_file() or not path.name.startswith("back-"):
            continue
        stem = path.name.removesuffix(".md")
        # Split on "-to-" to separate the from-phase from the to-phase+n.
        # e.g. "back-implement-to-plan-1" -> ["back-implement", "plan-1"]
        if "-to-" not in stem:
            continue
        _from_part, _, to_part = stem.partition("-to-")
        # to_part is "<to>-<n>"; the to-phase is everything before the last "-<n>".
        # Phase names may contain hyphens (e.g. "code-review"), so split from the right.
        target = to_part.rsplit("-", 1)[0] if "-" in to_part else to_part
        counts[target] = counts.get(target, 0) + 1
    return counts


def check_backward_edge_counts(run_dir: Path) -> list[Finding]:
    """Check that backward edge counts in the manifest match the back-*.md files on disk."""
    findings: list[Finding] = []
    text = _read_manifest(run_dir)
    if text is None:
        return []

    manifest_counts = _parse_backward_edge_counts_from_manifest(text)
    disk_counts = _parse_backward_edge_counts_from_disk(run_dir)

    for phase in ("clarify", "research", "plan", "implement", "code-review"):
        manifest_count = manifest_counts.get(phase, 0)
        disk_count = disk_counts.get(phase, 0)
        if phase in manifest_counts:
            # Manifest recorded a count for this phase — it must match disk.
            if manifest_count != disk_count:
                findings.append(Finding(
                    severity="error",
                    check="manifest_state",
                    message=(
                        f"Backward edge count mismatch for {phase}: "
                        f"manifest={manifest_count}, disk={disk_count}"
                    ),
                ))
        elif disk_count > 0:
            # No manifest entry for this phase, but packets exist on disk —
            # the manifest is out of sync with the run directory.
            findings.append(Finding(
                severity="error",
                check="manifest_state",
                message=(
                    f"Backward packets on disk for {phase} ({disk_count}) but "
                    f"manifest has no 'Backward edges received' entry"
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
